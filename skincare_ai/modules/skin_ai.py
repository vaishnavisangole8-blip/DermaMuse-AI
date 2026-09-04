"""
Module 4 & 5 – AI Skin Concern Classification + Numerical Skin Scoring

Provides two backends:
  1. Real CNN/Transfer Learning model  (USE_MOCK_AI = False)
  2. Rule-based mock analysis          (USE_MOCK_AI = True)   ← default for dev

The mock backend combines questionnaire sliders with lightweight
OpenCV image feature extraction (brightness, saturation variance)
so it still processes the actual uploaded photo.

Overall Score formula (as documented in project report):
  Overall = 0.30×SkinProfileScore + 0.25×ConcernScore
          + 0.20×RoutineCompat    + 0.15×ProductCompat
          + 0.10×BudgetCompat

For the analysis step we compute:
  Overall ≈ 100 - weighted_concern_penalty
"""

import os
import random
import math
import cv2
import numpy as np
from flask import current_app


# ── Image pre-processing ──────────────────────────────────────────────────────

def preprocess_image(image_path: str, target_size=(224, 224)):
    """Load, resize, normalise image. Returns numpy array (1,H,W,3)."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")
    img = cv2.resize(img, target_size)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img_rgb.astype(np.float32) / 255.0, img   # normalised, original


def extract_image_features(img_bgr: np.ndarray) -> dict:
    """
    Extract basic visual features from the face image using OpenCV.
    These feed into the mock scoring when no trained model is available.
    """
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    # Brightness (value channel mean)
    brightness = float(np.mean(v)) / 255.0          # 0-1, higher = brighter

    # Saturation variance → proxy for redness/unevenness
    sat_mean   = float(np.mean(s)) / 255.0
    sat_std    = float(np.std(s))  / 255.0

    # Skin region approximate sheen (oiliness proxy via high-brightness patches)
    bright_mask = (v > 200).astype(np.uint8)
    sheen_ratio = float(np.sum(bright_mask)) / bright_mask.size

    # Texture roughness via Laplacian variance (dryness / acne proxy)
    gray      = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    texture_var = float(np.var(laplacian)) / 10000.0   # normalise roughly 0-1

    return {
        'brightness': min(brightness, 1.0),
        'sat_mean':   min(sat_mean,   1.0),
        'sat_std':    min(sat_std,    1.0),
        'sheen_ratio':min(sheen_ratio,1.0),
        'texture_var':min(texture_var,1.0),
    }


# ── Mock AI scorer ─────────────────────────────────────────────────────────────

def _clamp(val, lo=0, hi=100):
    return max(lo, min(hi, int(round(val))))


def mock_analyze(questionnaire: dict, image_path) -> dict:
    """
    Rule-based analysis combining questionnaire + image features.
    If image_path is None, uses questionnaire only.
    Returns scores dict (all 0-100).
    """
    # --- Questionnaire inputs (0-10 sliders → 0-100 scale)
    q_oil  = questionnaire.get('q_oiliness',     5) * 10
    q_dry  = questionnaire.get('q_dryness',       5) * 10
    q_sens = questionnaire.get('q_sensitivity',   5) * 10
    q_acne = questionnaire.get('q_acne_concern',  5) * 10
    sun    = {'Low': 0, 'Medium': 30, 'High': 60}.get(
               questionnaire.get('sun_exposure', 'Medium'), 30)
    skin_type = questionnaire.get('skin_type', 'Normal')

    # --- Image features (only if image provided)
    if image_path:
        try:
            _, img_bgr = preprocess_image(image_path)
            feat = extract_image_features(img_bgr)
            sheen   = feat['sheen_ratio']   * 100
            texture = feat['texture_var']   * 100
            redness = feat['sat_mean']      * 100
            bright  = feat['brightness']    * 100
            has_image = True
        except Exception:
            sheen, texture, redness, bright = 40, 30, 30, 60
            has_image = False
    else:
        # No image — derive from questionnaire only
        sheen   = q_oil  * 0.8
        texture = q_acne * 0.9
        redness = q_sens * 0.7
        bright  = 65
        has_image = False

    # --- Blend questionnaire + image features
    if has_image:
        oiliness  = _clamp(0.6 * q_oil  + 0.4 * sheen)
        dryness   = _clamp(0.6 * q_dry  + 0.4 * max(0, 80 - bright))
        acne      = _clamp(0.6 * q_acne + 0.4 * texture)
        redness_s = _clamp(0.5 * q_sens + 0.5 * redness)
    else:
        # Questionnaire only — direct mapping
        oiliness  = _clamp(q_oil  + random.randint(-5, 5))
        dryness   = _clamp(q_dry  + random.randint(-5, 5))
        acne      = _clamp(q_acne + random.randint(-5, 5))
        redness_s = _clamp(q_sens + random.randint(-5, 5))

    pigment   = _clamp(0.4 * sun + 0.3 * redness_s + 0.3 * q_sens)

    # Skin-type adjustments
    adjustments = {
        'Oily':        {'oiliness': +10, 'dryness': -10},
        'Dry':         {'oiliness': -10, 'dryness': +10},
        'Combination': {'oiliness':  +5, 'dryness':  +5},
        'Normal':      {},
    }
    adj = adjustments.get(skin_type, {})
    oiliness  = _clamp(oiliness  + adj.get('oiliness', 0))
    dryness   = _clamp(dryness   + adj.get('dryness',  0))

    # Small realistic noise (±5)
    def jitter(v):
        return _clamp(v + random.randint(-5, 5))

    oiliness  = jitter(oiliness)
    dryness   = jitter(dryness)
    acne      = jitter(acne)
    redness_s = jitter(redness_s)
    pigment   = jitter(pigment)

    # Overall score (inverse of concern average)
    concern_avg = (oiliness + dryness + acne + redness_s) / 4
    overall = _clamp(100 - 0.6 * concern_avg + 0.4 * (100 - concern_avg) * 0.3)

    # Confidence based on image quality proxy
    confidence = _clamp(65 + (bright / 5)) if image_path else 72

    # Skin profile label
    profile = _build_profile(skin_type, oiliness, dryness, acne, redness_s)

    return {
        'oiliness_score':    oiliness,
        'dryness_score':     dryness,
        'concern_score':     acne,
        'sensitivity_score': redness_s,
        'redness_score':     redness_s,
        'pigmentation_score':pigment,
        'overall_score':     overall,
        'confidence':        confidence,
        'skin_profile':      profile,
    }


def _build_profile(skin_type, oiliness, dryness, acne, sensitivity) -> str:
    parts = [skin_type]
    if acne > 60:
        parts.append('Acne-prone')
    if sensitivity > 65:
        parts.append('Sensitive')
    if oiliness > 70 and dryness > 50:
        parts[0] = 'Combination'
    return ' / '.join(parts)


# ── Real model scorer ──────────────────────────────────────────────────────────

def real_model_analyze(questionnaire: dict, image_path: str) -> dict:
    """
    Placeholder for actual CNN/Transfer Learning model inference.
    Replace the body of this function once model is trained and saved.

    Expected model output: array of shape (1, 5)
    Indices: [oiliness, dryness, acne, redness, pigmentation]  (0-1 probabilities)
    """
    try:
        import tensorflow as tf
        model_path = current_app.config.get('MODEL_PATH', '')
        if not os.path.exists(model_path):
            raise FileNotFoundError("Model file not found, falling back to mock.")

        model = tf.keras.models.load_model(model_path)
        img_array, _ = preprocess_image(image_path)
        img_input = np.expand_dims(img_array, axis=0)
        preds = model.predict(img_input)[0]   # shape (5,)

        oiliness  = _clamp(preds[0] * 100)
        dryness   = _clamp(preds[1] * 100)
        acne      = _clamp(preds[2] * 100)
        redness   = _clamp(preds[3] * 100)
        pigment   = _clamp(preds[4] * 100)

        concern_avg = (oiliness + dryness + acne + redness) / 4
        overall     = _clamp(100 - 0.6 * concern_avg)
        confidence  = 88   # replace with model's own confidence if available

        q = questionnaire
        profile = _build_profile(q.get('skin_type','Normal'),
                                  oiliness, dryness, acne, redness)
        return {
            'oiliness_score':    oiliness,
            'dryness_score':     dryness,
            'concern_score':     acne,
            'sensitivity_score': redness,
            'redness_score':     redness,
            'pigmentation_score':pigment,
            'overall_score':     overall,
            'confidence':        confidence,
            'skin_profile':      profile,
        }
    except Exception as e:
        current_app.logger.warning(f"Real model failed ({e}), using mock.")
        return mock_analyze(questionnaire, image_path)


# ── Public API ────────────────────────────────────────────────────────────────

def analyze_skin(questionnaire: dict, image_path) -> dict:
    """
    Main entry point called by Flask routes.
    image_path can be None — questionnaire-only analysis will run.
    """
    use_mock = current_app.config.get('USE_MOCK_AI', True)
    if use_mock:
        return mock_analyze(questionnaire, image_path)
    return real_model_analyze(questionnaire, image_path)
