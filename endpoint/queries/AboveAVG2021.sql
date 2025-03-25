with department_hires as (
    select 
        d.id,
        d.department,
        count(he.id) as hired
    from departments d
    left join hired_employees he 
        on d.id = he.department_id 
        and extract(year from he.datetime::timestamp) = 2021
    group by d.id, d.department
),
average_hires as (
    select avg(hired) as avg_hired from department_hires
)
select 
    dh.id,
    dh.department,
    dh.hired
from department_hires dh, average_hires ah
where dh.hired > ah.avg_hired
order by dh.hired desc;