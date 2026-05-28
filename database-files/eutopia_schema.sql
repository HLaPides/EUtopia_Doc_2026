-- EUtopia Database DDL
-- Lesson-centered schema based on the provided ERD

DROP TABLE IF EXISTS Response;
DROP TABLE IF EXISTS Question;
DROP TABLE IF EXISTS Assessment;
DROP TABLE IF EXISTS StudentProgress;
DROP TABLE IF EXISTS Simulation;
DROP TABLE IF EXISTS DiagnosticSurvey;
DROP TABLE IF EXISTS Lessons;
DROP TABLE IF EXISTS Student;
DROP TABLE IF EXISTS Class;
DROP TABLE IF EXISTS Teacher;
DROP TABLE IF EXISTS EUOfficial;
DROP TABLE IF EXISTS PlatformPerformance;

CREATE TABLE Teacher (
    teacherID INT PRIMARY KEY,
    countryOrigin VARCHAR(100),
    firstName VARCHAR(100) NOT NULL,
    lastName VARCHAR(100) NOT NULL,
    prefix VARCHAR(20)
);

CREATE TABLE Class (
    classID INT PRIMARY KEY,
    teacherID INT NOT NULL,
    className VARCHAR(100) NOT NULL,
    FOREIGN KEY (teacherID) REFERENCES Teacher(teacherID)
);

CREATE TABLE Student (
    studentID INT PRIMARY KEY,
    countryOrigin VARCHAR(100),
    age INT,
    surveyScore DECIMAL(5,2),
    classID INT,
    firstName VARCHAR(100) NOT NULL,
    lastName VARCHAR(100) NOT NULL,
    FOREIGN KEY (classID) REFERENCES Class(classID)
);

CREATE TABLE EUOfficial (
    officialID INT PRIMARY KEY,
    originCountry VARCHAR(100),
    firstName VARCHAR(100) NOT NULL,
    lastName VARCHAR(100) NOT NULL
);

CREATE TABLE Lessons (
    lessonID INT PRIMARY KEY,
    classID INT,
    approvalStatus VARCHAR(50) DEFAULT 'Pending',
    content TEXT NOT NULL,
    teacherID INT NOT NULL,
    approvedBy INT,
    topicName VARCHAR(100),
    title VARCHAR(150) NOT NULL,
    difficultyLevel VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (classID) REFERENCES Class(classID),
    FOREIGN KEY (teacherID) REFERENCES Teacher(teacherID),
    FOREIGN KEY (approvedBy) REFERENCES EUOfficial(officialID)
);

CREATE TABLE Assessment (
    assessmentID INT PRIMARY KEY,
    lessonID INT NOT NULL,
    assessmentType VARCHAR(50) NOT NULL,
    maxScore DECIMAL(5,2),
    FOREIGN KEY (lessonID) REFERENCES Lessons(lessonID)
);

CREATE TABLE Question (
    questionID INT PRIMARY KEY,
    assessmentID INT NOT NULL,
    questionText TEXT NOT NULL,
    questionType VARCHAR(50),
    FOREIGN KEY (assessmentID) REFERENCES Assessment(assessmentID)
);

CREATE TABLE Response (
    responseID INT PRIMARY KEY,
    input TEXT,
    studentID INT NOT NULL,
    questionID INT NOT NULL,
    score DECIMAL(5,2),
    FOREIGN KEY (studentID) REFERENCES Student(studentID),
    FOREIGN KEY (questionID) REFERENCES Question(questionID)
);

CREATE TABLE StudentProgress (
    progressID INT PRIMARY KEY,
    completionRates DECIMAL(5,2),
    quizPerformance DECIMAL(5,2),
    avgEngagementTime DECIMAL(8,2),
    studentID INT NOT NULL,
    lessonID INT NOT NULL,
    completionStatus VARCHAR(50),
    FOREIGN KEY (studentID) REFERENCES Student(studentID),
    FOREIGN KEY (lessonID) REFERENCES Lessons(lessonID)
);

CREATE TABLE Simulation (
    simulationID INT PRIMARY KEY,
    countryName VARCHAR(100),
    population BIGINT,
    gdpPerCapita DECIMAL(12,2),
    studentID INT NOT NULL,
    unemploymentRate DECIMAL(5,2),
    compulsoryVoting BOOLEAN,
    yearsMembership INT,
    corruptionIndex DECIMAL(5,2),
    urbanizationRate DECIMAL(5,2),
    medianAge DECIMAL(5,2),
    netBeneficiary BOOLEAN,
    weekendVoting BOOLEAN,
    predictedTurnout DECIMAL(5,2),
    FOREIGN KEY (studentID) REFERENCES Student(studentID)
);

CREATE TABLE DiagnosticSurvey (
    surveyID INT PRIMARY KEY,
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
    FOREIGN KEY (studentID) REFERENCES Student(studentID),
    FOREIGN KEY (lessonID) REFERENCES Lessons(lessonID)
);

CREATE TABLE PlatformPerformance (
    performanceID INT PRIMARY KEY,
    numActiveUsers INT DEFAULT 0,
    completionRates DECIMAL(5,2),
    numLessonsCreated INT DEFAULT 0,
    numLessonsApproved INT DEFAULT 0
);
