-- ============================================================
-- AI SkinCare Analyzer - Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS skincare_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE skincare_ai;

-- ============================================================
-- Table: users
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    user_id     INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100)        NOT NULL,
    email       VARCHAR(150)        NOT NULL UNIQUE,
    password    VARCHAR(255)        NOT NULL,   -- bcrypt hash
    age_group   ENUM('13-17','18-24','25-34','35-44','45+') DEFAULT '18-24',
    created_at  DATETIME            DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME            DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================================
-- Table: skin_analyses
-- ============================================================
CREATE TABLE IF NOT EXISTS skin_analyses (
    analysis_id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id             INT             NOT NULL,
    analysis_date       DATETIME        DEFAULT CURRENT_TIMESTAMP,

    -- Questionnaire inputs
    skin_type           ENUM('Normal','Dry','Oily','Combination') DEFAULT 'Normal',
    q_oiliness          TINYINT UNSIGNED DEFAULT 5,   -- 0-10 slider
    q_dryness           TINYINT UNSIGNED DEFAULT 5,
    q_sensitivity       TINYINT UNSIGNED DEFAULT 5,
    q_acne_concern      TINYINT UNSIGNED DEFAULT 5,
    sun_exposure        ENUM('Low','Medium','High') DEFAULT 'Medium',
    budget              INT UNSIGNED    DEFAULT 1500,  -- INR

    -- AI image analysis scores (0-100)
    oiliness_score      TINYINT UNSIGNED DEFAULT 0,
    dryness_score       TINYINT UNSIGNED DEFAULT 0,
    sensitivity_score   TINYINT UNSIGNED DEFAULT 0,
    concern_score       TINYINT UNSIGNED DEFAULT 0,   -- acne/blemish concern
    redness_score       TINYINT UNSIGNED DEFAULT 0,
    pigmentation_score  TINYINT UNSIGNED DEFAULT 0,
    overall_score       TINYINT UNSIGNED DEFAULT 0,   -- 0-100
    confidence          TINYINT UNSIGNED DEFAULT 0,   -- analysis confidence %

    -- Derived profile
    skin_profile        VARCHAR(100)    DEFAULT '',   -- e.g. "Oily / Acne-prone"

    -- Image reference (filename only, not full path)
    image_filename      VARCHAR(255)    DEFAULT NULL,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================
-- Table: products
-- ============================================================
CREATE TABLE IF NOT EXISTS products (
    product_id      INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(200)    NOT NULL,
    brand           VARCHAR(100)    NOT NULL,
    category        ENUM('Cleanser','Moisturizer','Sunscreen','Serum','Toner',
                         'Exfoliator','Eye Cream','Face Mask','Treatment','Other')
                    NOT NULL,
    price           INT UNSIGNED    NOT NULL,   -- INR
    description     TEXT,
    ingredients     TEXT,           -- comma-separated key ingredients
    skin_types      VARCHAR(100),   -- comma-separated: Oily,Dry,Normal,Combination
    concern_tags    VARCHAR(200),   -- comma-separated: Acne,Redness,Dryness,Pigmentation,Oiliness,Sensitivity
    rating          DECIMAL(2,1)    DEFAULT 4.0,  -- out of 5
    image_url       VARCHAR(255)    DEFAULT NULL,
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Table: recommendations
-- ============================================================
CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id   INT AUTO_INCREMENT PRIMARY KEY,
    user_id             INT         NOT NULL,
    analysis_id         INT         NOT NULL,
    product_id          INT         NOT NULL,
    skin_match          TINYINT UNSIGNED DEFAULT 0,    -- 0-100
    concern_match       TINYINT UNSIGNED DEFAULT 0,
    budget_match        TINYINT UNSIGNED DEFAULT 0,
    final_score         TINYINT UNSIGNED DEFAULT 0,
    routine_slot        ENUM('Day','Night','Both','Optional') DEFAULT 'Both',
    created_at          DATETIME    DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)    REFERENCES users(user_id)     ON DELETE CASCADE,
    FOREIGN KEY (analysis_id) REFERENCES skin_analyses(analysis_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- ============================================================
-- Table: chat_history
-- ============================================================
CREATE TABLE IF NOT EXISTS chat_history (
    chat_id     INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT         NOT NULL,
    role        ENUM('user','bot') NOT NULL,
    message     TEXT        NOT NULL,
    created_at  DATETIME    DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================
-- Table: ingredients_info  (Ingredient Analyzer)
-- ============================================================
CREATE TABLE IF NOT EXISTS ingredients_info (
    ingredient_id   INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100)    NOT NULL UNIQUE,
    common_use      TEXT,
    suitable_for    VARCHAR(200),   -- skin types/profiles
    avoid_for       VARCHAR(200),
    compatibility   TINYINT UNSIGNED DEFAULT 80,  -- general score 0-100
    description     TEXT
);

-- ============================================================
-- Indexes for performance
-- ============================================================
CREATE INDEX idx_analyses_user ON skin_analyses(user_id);
CREATE INDEX idx_recommendations_user ON recommendations(user_id);
CREATE INDEX idx_chat_user ON chat_history(user_id);
CREATE INDEX idx_products_category ON products(category);
