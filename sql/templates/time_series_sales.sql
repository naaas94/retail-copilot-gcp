-- Time Series Sales Query Template
-- Intent: net_sales time series by dimension (store/region/category)
-- Parameters: time_grain, dimension, start_date, end_date, tenant_id, row_limit

SELECT 
  DATE_TRUNC({{time_grain}}, s.order_date) AS dt,
  {% if dimension_column %}
  {{dimension_table}}.{{dimension_column}} AS {{dimension_name}},
  {% endif %}
  SUM(s.gross_sales - s.returns - s.discounts) AS net_sales,
  COUNT(DISTINCT s.transaction_id) AS transaction_count
FROM {{dataset}}.fct_sales s
{% if dimension_table %}
JOIN {{dataset}}.{{dimension_table}} d ON d.{{join_key}} = s.{{join_key}}
{% endif %}
WHERE s.tenant_id = '{{tenant_id}}'
  AND s.order_date BETWEEN '{{start_date}}' AND '{{end_date}}'
  {% if exclude_returns %}
  AND s.returns = 0
  {% endif %}
  {% if category_filter %}
  AND d.category IN ({{category_filter}})
  {% endif %}
GROUP BY 1{% if dimension_column %}, 2{% endif %}
ORDER BY 1{% if dimension_column %}, 2{% endif %}
LIMIT {{row_limit}};

