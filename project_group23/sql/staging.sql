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

-- select ben.job_id, GROUP_CONCAT(ben.type SEPARATOR '; ') as job_benefits
-- from jobs_benefits ben
-- group by
--     job_id
-- limit 1000;