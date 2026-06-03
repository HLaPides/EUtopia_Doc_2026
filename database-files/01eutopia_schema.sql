-- EUtopia Database DDL
-- Lesson-centered schema based on the provided ERD

DROP TABLE IF EXISTS Response;
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

CREATE TABLE Users (
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

CREATE TABLE Role (
    roleID INT AUTO_INCREMENT PRIMARY KEY,
    roleName VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE UserRole (
    userID INT NOT NULL,
    roleID INT NOT NULL,
    PRIMARY KEY (userID, roleID),
    FOREIGN KEY (userID) REFERENCES Users(userID),
    FOREIGN KEY (roleID) REFERENCES Role(roleID)
);

CREATE TABLE Class (
    classID INT AUTO_INCREMENT PRIMARY KEY,
    teacherID INT NOT NULL,
    className VARCHAR(100) NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    createdBy INT,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updatedBy INT,
    FOREIGN KEY (teacherID) REFERENCES Users(userID)
);

CREATE TABLE StudentProfile (
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

CREATE TABLE Lessons (
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

CREATE TABLE Assessment (
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

CREATE TABLE Question (
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

CREATE TABLE Response (
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

CREATE TABLE StudentProgress (
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

CREATE TABLE Simulation (
    simulationID INT AUTO_INCREMENT PRIMARY KEY,
    studentID INT NOT NULL,
    countryName VARCHAR(100),
    population BIGINT,
    gdpPerCapita DECIMAL(12,2),
    unemploymentRate DECIMAL(5,2),
    compulsoryVoting BOOLEAN,
    yearsMembership INT,
    corruptionIndex DECIMAL(5,2),
    urbanizationRate DECIMAL(5,2),
    medianAge DECIMAL(5,2),
    netBeneficiary BOOLEAN,
    weekendVoting BOOLEAN,
    predictedTurnout DECIMAL(5,2),
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    createdBy INT,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updatedBy INT,
    FOREIGN KEY (studentID) REFERENCES Users(userID)
);

CREATE TABLE DiagnosticSurvey (
    surveyID INT AUTO_INCREMENT PRIMARY KEY,
    studentID INT NOT NULL,
    lessonID INT,
    age INT,
    educationLevel VARCHAR(100),
    gender VARCHAR(50),
    politicalInterest VARCHAR(100),
    trustNationalParliament DECIMAL(5,2),
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

CREATE TABLE PlatformPerformance (
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