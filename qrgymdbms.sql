CREATE DATABASE gymqrs_qrsdb;

USE gymqrs_qrsdb;

-- جدول المستخدمين
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    is_premium BOOLEAN DEFAULT FALSE,
    gym_id VARCHAR(50),  -- المستخدم العادي بياخده من الجيم
    premium_id VARCHAR(50),  -- المستخدم البريميوم بياخده عند الاشتراك
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول الكباتن
CREATE TABLE trainers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول الأجهزة الرياضية
CREATE TABLE gym_equipment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    qr_code TEXT NOT NULL, -- ممكن نخزن هنا البيانات أو اللينك اللي فيه شرح التمرين
    target_muscles VARCHAR(200), -- العضلات المستهدفة
    description TEXT,
    video_link TEXT,
    gym_location VARCHAR(100) -- لو عايز تربط جهاز بمكان معين في الجيم
);

-- جدول التمارين المرتبطة بالمستخدم
CREATE TABLE user_workouts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    equipment_id INT,
    workout_date DATE,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (equipment_id) REFERENCES gym_equipment(id) ON DELETE SET NULL
);

-- جدول متابعة الكابتن للمستخدمين
CREATE TABLE trainer_tracking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trainer_id INT,
    user_id INT,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trainer_id) REFERENCES trainers(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- جدول OTP أو كود التفعيل
CREATE TABLE otp_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    code VARCHAR(10),
    method ENUM('email', 'phone'),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
