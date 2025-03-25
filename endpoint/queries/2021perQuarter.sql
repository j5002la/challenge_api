select 
    d.department as department,
    j.job as job,
    sum(case when extract(quarter from he.datetime::timestamp) = 1 then 1 else 0 end) as q1,
    sum(case when extract(quarter from he.datetime::timestamp) = 2 then 1 else 0 end) as q2,
    sum(case when extract(quarter from he.datetime::timestamp) = 3 then 1 else 0 end) as q3,
    sum(case when extract(quarter from he.datetime::timestamp) = 4 then 1 else 0 end) as q4
from hired_employees he
join departments d on he.department_id = d.id
join jobs j on he.job_id = j.id
where extract(year from he.datetime::timestamp) = 2021
group by d.department, j.job
order by d.department, j.job;
