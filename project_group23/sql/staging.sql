-- Active: 1779702172225@@3de0dac0-8513-4220-9ee7-414dc040c138.bn2a2uid0up8mv7mv2ig.databases.appdomain.cloud@31131@linkedin_jobs
--session 1 e 2
-- select *
-- from linkedin_jobs.postings post
--     inner join (
--         select ben.job_id, GROUP_CONCAT(ben.type SEPARATOR '; ') as job_benefits
--         from linkedin_jobs.jobs_benefits ben
--         group by
--             job_id
--     ) ben on post.job_id = ben.job_id
-- where
--     post.closed_time is null
-- limit 100;

create table a20254350.postings_with_benefits as
select post.*, ben.job_benefits as benefits
from postings post
    left join (
        select ben.job_id, GROUP_CONCAT(ben.type SEPARATOR '; ') as job_benefits
        from jobs_benefits ben
        group by
            job_id
    ) ben on post.job_id = ben.job_id
where
    post.closed_time is null;

# Example 1: Question: Which companies have the most job postings?

# #This query identifies the top 10 companies with the highest number of job postings in the postings table. It helps show which companies are the most active recruiters in the dataset. In this case, it’s Liberty Healthcare and Rehabilition Services, with 1059.

SELECT  
    COALESCE(c.name, p.company_name) AS company_name, 
    COUNT(*) AS job_count 
FROM linkedin_jobs.postings p 
LEFT JOIN linkedin_jobs.companies_companies c 
    ON p.company_id = c.company_id 
GROUP BY COALESCE(c.name, p.company_name) 
ORDER BY job_count DESC 
LIMIT 10;

# Example 2: Question: What are the most common skills for Data Analyst jobs?

## This query finds the top 10 skills most frequently linked to job postings with “Data Analyst” in the title. It helps identify the technical or professional skills most commonly requested for Data Analyst roles. One can see IT is the most common skill, followed from afar by Analyst.

SELECT  
    ms.skill_name, 
    COUNT(DISTINCT p.job_id) AS job_count 
FROM linkedin_jobs.postings p 
INNER JOIN linkedin_jobs.jobs_job_skills jsk 
    ON p.job_id = jsk.job_id 
INNER JOIN linkedin_jobs.mappings_skills ms 
    ON jsk.skill_abr = ms.skill_abr 
WHERE p.title LIKE '%%Data Analyst%%' 
GROUP BY ms.skill_name 
ORDER BY job_count DESC 
LIMIT 10;

# Example 3: Question: What is the average normalized salary by experience level?

## This query calculates the average normalized salary for each experience level and shows how many postings are included in each group. It helps compare salary differences between experience levels, such as entry-level, mid-senior, or executive roles.

###The salary-by-experience query showed that Entry level roles had the highest average normalized salary. However, after inspecting the highest salary values, this result appears to be affected by extreme outliers in the normalized_salary column. Therefore, the query is correct syntactically and logically, but the interpretation of the result should be cautious.

SELECT 
    p.formatted_experience_level, 
    COUNT(*) AS job_count, 
    ROUND(AVG(p.normalized_salary), 2) AS avg_normalized_salary 
FROM linkedin_jobs.postings p 
WHERE p.normalized_salary IS NOT NULL 
  AND p.formatted_experience_level IS NOT NULL 
  AND TRIM(p.formatted_experience_level) <> '' 
GROUP BY p.formatted_experience_level 
ORDER BY avg_normalized_salary DESC;