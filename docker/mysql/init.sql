-- 데이터베이스 생성 및 선택
CREATE DATABASE IF NOT EXISTS behero;
USE behero;

-- Users 테이블 생성
-- 기본적인 사용자 정보를 저장하는 테이블입니다.
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20),
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    profile_img VARCHAR(255),
    join_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email)  -- 로그인에 사용되므로 인덱스 추가
);

-- Heroes 테이블 생성
-- 사용자의 게임 캐릭터 정보를 저장하는 테이블입니다.
CREATE TABLE IF NOT EXISTS heroes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE,  -- 1:1 관계를 위한 UNIQUE 제약조건
    hero_level INT DEFAULT 1,
    coin INT DEFAULT 0,
    avatar_id INT DEFAULT 0,
    background_id INT DEFAULT 0,
    tag JSON,  -- MySQL 5.7 이상에서 지원하는 JSON 타입 사용
    did_info JSON,  -- 업적 정보도 JSON으로 저장
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
);

-- Stories 테이블 생성
-- 사용자의 스토리(일기) 정보를 저장하는 테이블입니다.
CREATE TABLE IF NOT EXISTS stories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    contents TEXT,  -- 긴 텍스트를 저장하기 위해 TEXT 타입 사용
    img VARCHAR(255),  -- 이미지 URL 저장
    create_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id_create_at (user_id, create_at)  -- 사용자별 시간순 조회를 위한 복합 인덱스
);

-- Items 테이블 생성
-- 게임 내 아이템 정보를 저장하는 테이블입니다.
CREATE TABLE IF NOT EXISTS items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    price INT NOT NULL,
    item_type ENUM('avatar', 'background') NOT NULL,  -- 아이템 타입을 ENUM으로 제한
    INDEX idx_item_type (item_type)
);

-- Receipts 테이블 생성
-- 아이템 구매 기록을 저장하는 테이블입니다.
CREATE TABLE IF NOT EXISTS receipts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    item_id INT NOT NULL,
    purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    INDEX idx_user_purchases (user_id, purchase_date)
);

-- Quests 테이블 생성
-- 사용자의 퀘스트 정보를 저장하는 테이블입니다.
CREATE TABLE IF NOT EXISTS quests (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(30) NOT NULL,
    description VERCHAR(200) NOT NULL,
    tag JSON,  -- 태그 정보를 JSON으로 저장
    days JSON,  -- 요일 정보를 JSON으로 저장
    progress_time INT DEFAULT 0,
    complete_time INT DEFAULT 0,
    finish BOOLEAN DEFAULT FALSE,
    quest_type ENUM('self', 'ai') NOT NULL,
    start_time DATETIME,
    stop_time DATETIME,
    finish_time DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    deadline DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_quests (user_id, quest_type, finish)
);

-- Friends 테이블 생성
-- 사용자 간의 친구 관계를 저장하는 테이블입니다.
CREATE TABLE IF NOT EXISTS friends (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    friend_user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (friend_user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_friendship (user_id, friend_user_id),  -- 중복 친구 관계 방지
    INDEX idx_user_friends (user_id, created_at)
);
=
-- Groups 테이블 생성
-- 그룹 정보를 저장하는 테이블입니다.
CREATE TABLE IF NOT EXISTS `groups` (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_group_name (name)
);

-- Group_Members 테이블 생성
-- 그룹 멤버십 정보를 저장하는 테이블입니다.
CREATE TABLE IF NOT EXISTS group_members (
    id INT PRIMARY KEY AUTO_INCREMENT,
    group_id INT NOT NULL,
    user_id INT NOT NULL,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES `groups`(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_membership (group_id, user_id),
    INDEX idx_group_members (group_id, joined_at)
);

-- Admins 테이블 생성
-- 관리자 정보를 저장하는 테이블입니다.
CREATE TABLE IF NOT EXISTS admins (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_admin (user_id)  -- 중복 관리자 방지
);

-- 기본 인덱스 생성
CREATE INDEX idx_hero_level ON heroes(hero_level);
CREATE INDEX idx_quest_status ON quests(finish, start_time);
CREATE INDEX idx_group_creation ON groups(created_at);