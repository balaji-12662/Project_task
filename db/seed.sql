-- db/seed.sql
-- Minimal seed (20 employees, 2 closed cycles)
-- Insert employees
INSERT INTO employees (name, email, department, manager_id, hire_date, role)
VALUES
('Alice Johnson','alice.johnson@techcorp.com','Engineering', NULL, '2018-03-15', 'director'),
('Bob Singh','bob.singh@techcorp.com','Engineering', 1, '2019-06-10', 'manager'),
('Carol Lee','carol.lee@techcorp.com','Engineering', 2, '2020-01-05', 'engineer'),
('David Kumar','david.kumar@techcorp.com','Engineering', 2, '2021-07-11', 'engineer'),
('Eve Patel','eve.patel@techcorp.com','Engineering', 2, '2022-04-21', 'engineer'),
('Frank Zhang','frank.zhang@techcorp.com','Marketing', 1, '2017-09-01', 'manager'),
('Grace Park','grace.park@techcorp.com','Marketing', 6, '2019-11-12', 'specialist'),
('Hiro Tanaka','hiro.tanaka@techcorp.com','Marketing', 6, '2020-08-16', 'specialist'),
('Isha Rao','isha.rao@techcorp.com','Sales', 1, '2016-05-23', 'manager'),
('Jonas Muller','jonas.muller@techcorp.com','Sales', 9, '2018-02-12', 'executive'),
('Kiran Das','kiran.das@techcorp.com','HR', 1, '2015-12-01', 'hr'),
('Lina Gomez','lina.gomez@techcorp.com','Engineering', 2, '2019-05-14', 'engineer'),
('Manish Joshi','manish.joshi@techcorp.com','Engineering', 2, '2020-09-09', 'engineer'),
('Nora White','nora.white@techcorp.com','Finance', 1, '2018-10-30', 'manager'),
('Omar Ali','omar.ali@techcorp.com','Finance', 14, '2021-03-18', 'analyst'),
('Priya Mehta','priya.mehta@techcorp.com','Engineering', 2, '2021-12-22', 'engineer'),
('Quinn Brooks','quinn.brooks@techcorp.com','Support', 1, '2019-04-02', 'lead'),
('Ravi Sharma','ravi.sharma@techcorp.com','Engineering', 2, '2023-01-15', 'intern'),
('Sana Khan','sana.khan@techcorp.com','Marketing', 6, '2022-06-06', 'intern'),
('Tom O\'Neil','tom.oneil@techcorp.com','Engineering', 2, '2016-08-24', 'senior_engineer');

-- Insert two cycles (completed)
INSERT INTO review_cycles (name, start_date, end_date, status)
VALUES ('2024 Q1', '2024-01-01','2024-03-31','closed'),
       ('2024 Q2', '2024-04-01','2024-06-30','closed');

-- Example reviews+scores for a couple of employees in both cycles
-- Employee 3 (Carol) - self, manager, two peer reviews for both cycles
INSERT INTO reviews (employee_id, reviewer_id, cycle_id, review_type, status, submitted_date)
VALUES
(3, 3, 1, 'self', 'submitted', '2024-04-02 09:00:00'),
(3, 2, 1, 'manager', 'submitted', '2024-04-03 10:00:00'),
(3, 4, 1, 'peer', 'submitted', '2024-04-04 11:00:00'),
(3, 5, 1, 'peer', 'submitted', '2024-04-04 12:00:00'),
(3, 3, 2, 'self', 'submitted', '2024-07-02 09:00:00'),
(3, 2, 2, 'manager', 'submitted', '2024-07-03 10:00:00'),
(3, 4, 2, 'peer', 'submitted', '2024-07-04 11:00:00'),
(3, 5, 2, 'peer', 'submitted', '2024-07-04 12:00:00');

-- Scores for the first review (review_id will vary, assume sequence; in real seed use INSERT ... RETURNING)
-- For illustration we assume review ids 1..8; adjust in your DB or use a management script (recommended).
-- Because raw SQL with returned IDs is hard here, prefer the Django management command (seed_data.py) below
-- which will create consistent reviews and scores programmatically.
