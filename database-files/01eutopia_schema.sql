DROP DATABASE IF EXISTS eutopia_db;
CREATE DATABASE IF NOT EXISTS eutopia_db;



CREATE DATABASE IF NOT EXISTS eutopia_db;
USE eutopia_db;

DROP TABLE IF EXISTS Response;
DROP TABLE IF EXISTS QuestionOption;
DROP TABLE IF EXISTS Question;
DROP TABLE IF EXISTS Assessment;
DROP TABLE IF EXISTS StudentProgress;
DROP TABLE IF EXISTS Simulation;
DROP TABLE IF EXISTS DiagnosticSurvey;
DROP TABLE IF EXISTS Lessons;
DROP TABLE IF EXISTS StudentProfile;
DROP TABLE IF EXISTS Class;
DROP TABLE IF EXISTS UserRole;
DROP TABLE IF EXISTS Role;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS PlatformPerformance;
DROP TABLE IF EXISTS voter_turnout_scaler;
DROP TABLE IF EXISTS voter_turnout_params;
DROP TABLE IF EXISTS eu_trust_params;

CREATE TABLE IF NOT EXISTS Users (
    userID INT AUTO_INCREMENT PRIMARY KEY,
    firstName VARCHAR(100) NOT NULL,
    lastName VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    countryOrigin VARCHAR(100),
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    createdBy INT,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updatedBy INT
);

CREATE TABLE IF NOT EXISTS Roles (
    roleID INT AUTO_INCREMENT PRIMARY KEY,
    roleName VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS UserRole (
    userID INT NOT NULL,
    roleID INT NOT NULL,
    PRIMARY KEY (userID, roleID),
    FOREIGN KEY (userID) REFERENCES Users(userID),
    FOREIGN KEY (roleID) REFERENCES Roles(roleID)
);

CREATE TABLE IF NOT EXISTS Class (
    classID INT AUTO_INCREMENT PRIMARY KEY,
    teacherID INT NOT NULL,
    className VARCHAR(100) NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    createdBy INT,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updatedBy INT,
    FOREIGN KEY (teacherID) REFERENCES Users(userID)
);

CREATE TABLE IF NOT EXISTS StudentProfile (
    studentID INT PRIMARY KEY,
    age INT,
    surveyScore DECIMAL(5,2),
    classID INT,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    createdBy INT,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updatedBy INT,
    FOREIGN KEY (studentID) REFERENCES Users(userID),
    FOREIGN KEY (classID) REFERENCES Class(classID)
);

CREATE TABLE IF NOT EXISTS Lessons (
    lessonID INT AUTO_INCREMENT PRIMARY KEY,
    classID INT,
    teacherID INT NOT NULL,
    approvedBy INT,
    title VARCHAR(150) NOT NULL,
    topicName VARCHAR(100),
    content TEXT NOT NULL,
    difficultyLevel VARCHAR(50),
    approvalStatus VARCHAR(50) DEFAULT 'Pending',
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    createdBy INT,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updatedBy INT,
    FOREIGN KEY (classID) REFERENCES Class(classID),
    FOREIGN KEY (teacherID) REFERENCES Users(userID),
    FOREIGN KEY (approvedBy) REFERENCES Users(userID)
);

CREATE TABLE IF NOT EXISTS Assessment (
    assessmentID INT AUTO_INCREMENT PRIMARY KEY,
    lessonID INT NOT NULL,
    assessmentName VARCHAR(150) NOT NULL,
    assessmentType VARCHAR(50) NOT NULL,
    maxScore DECIMAL(5,2),
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    createdBy INT,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updatedBy INT,
    FOREIGN KEY (lessonID) REFERENCES Lessons(lessonID)
);

CREATE TABLE IF NOT EXISTS Question (
    questionID INT AUTO_INCREMENT PRIMARY KEY,
    assessmentID INT NOT NULL,
    questionText TEXT NOT NULL,
    questionType VARCHAR(50),
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    createdBy INT,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updatedBy INT,
    FOREIGN KEY (assessmentID) REFERENCES Assessment(assessmentID)
);

CREATE TABLE IF NOT EXISTS QuestionOption (
    optionID INT AUTO_INCREMENT PRIMARY KEY,
    questionID INT NOT NULL,
    optionText TEXT NOT NULL,
    isCorrect BOOLEAN DEFAULT 0,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    createdBy INT,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updatedBy INT,
    FOREIGN KEY (questionID) REFERENCES Question(questionID)
);


CREATE TABLE IF NOT EXISTS Response (
    responseID INT AUTO_INCREMENT PRIMARY KEY,
    studentID INT NOT NULL,
    questionID INT NOT NULL,
    input TEXT,
    score DECIMAL(5,2),
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    createdBy INT,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updatedBy INT,
    FOREIGN KEY (studentID) REFERENCES Users(userID),
    FOREIGN KEY (questionID) REFERENCES Question(questionID)
);

CREATE TABLE IF NOT EXISTS StudentProgress (
    progressID INT AUTO_INCREMENT PRIMARY KEY,
    studentID INT NOT NULL,
    lessonID INT NOT NULL,
    completionRate DECIMAL(5,2),
    quizPerformance DECIMAL(5,2),
    avgEngagementTime DECIMAL(8,2),
    completionStatus VARCHAR(50),
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    createdBy INT,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updatedBy INT,
    FOREIGN KEY (studentID) REFERENCES Users(userID),
    FOREIGN KEY (lessonID) REFERENCES Lessons(lessonID)
);

CREATE TABLE IF NOT EXISTS Simulation (
    simulationID INT AUTO_INCREMENT PRIMARY KEY,
    studentID INT NOT NULL,
    countryName VARCHAR(100),
    population BIGINT,
    unemploymentRate DECIMAL(5,2),
    compulsoryVoting BOOLEAN,
    medianAge DECIMAL(5,2),
    region VARCHAR(20),
    nationalTurnout DECIMAL(5,2),
    predictedTurnout DECIMAL(5,2),
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    createdBy INT,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updatedBy INT,
    FOREIGN KEY (studentID) REFERENCES Users(userID)
);

CREATE TABLE IF NOT EXISTS DiagnosticSurvey (
    surveyID INT AUTO_INCREMENT PRIMARY KEY,
    studentID INT NOT NULL,
    lessonID INT,
    educationLevel VARCHAR(100),
    politicalAffiliation VARCHAR(100),
    trustEuroParliament DECIMAL(5,2),
    trustPoliticians DECIMAL(5,2),
    satisfactionDemocracy DECIMAL(5,2),
    predictedTrust DECIMAL(5,2),
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    createdBy INT,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updatedBy INT,
    FOREIGN KEY (studentID) REFERENCES Users(userID),
    FOREIGN KEY (lessonID) REFERENCES Lessons(lessonID)
);

CREATE TABLE IF NOT EXISTS PlatformPerformance (
    performanceID INT AUTO_INCREMENT PRIMARY KEY,
    numActiveUsers INT DEFAULT 0,
    completionRates DECIMAL(5,2),
    numLessonsCreated INT DEFAULT 0,
    numLessonsApproved INT DEFAULT 0,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    createdBy INT,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updatedBy INT
);

CREATE TABLE IF NOT EXISTS voter_turnout_params (
    sequence_number INT PRIMARY KEY,
    beta_vals TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS voter_turnout_scaler (
    sequence_number INT PRIMARY KEY,
    feature_means TEXT NOT NULL,
    feature_stds  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS eu_trust_params (
    sequence_number INT PRIMARY KEY,
    coef_vals TEXT NOT NULL,
    intercept FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS eu_turnout_dataset (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    country             VARCHAR(5)     NOT NULL,
    year                INT            NOT NULL,
    voter_turnout       DECIMAL(5,2),
    population          BIGINT,
    gdp_per_capita      DECIMAL(12,2),
    unemployment_rate   DECIMAL(5,2),
    compulsory_voting   TINYINT(1),
    years_eu_membership INT,
    urbanization_rate   DECIMAL(5,2),
    median_age          DECIMAL(5,2),
    eu_net_beneficiary  TINYINT(1),
    weekend_voting      TINYINT(1),
    national_turnout    DECIMAL(5,2),
    region_northern     TINYINT(1),
    region_southern     TINYINT(1),
    region_western      TINYINT(1)
);

CREATE TABLE IF NOT EXISTS eurobarometer_dataset (
    id                     INT AUTO_INCREMENT PRIMARY KEY,
    country                VARCHAR(5),
    age                    DECIMAL(5,1),
    education              DECIMAL(5,1),
    gender                 TINYINT(1),
    political_interest     TINYINT(1),
    trust_parliament       TINYINT(1),
    trust_politicians      TINYINT(1),
    satisfaction_democracy TINYINT(1),
    left_right             DECIMAL(5,1),
    trust_eu               TINYINT(1)
);
