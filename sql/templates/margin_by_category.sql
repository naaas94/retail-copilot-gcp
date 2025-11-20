-- Margin by Category Query Template
-- Intent: margin_by_category
-- Parameters: start_date, end_date, tenant_id, category_filter, row_limit

SELECT 
  p.category,
  SUM(s.revenue) AS total_revenue,
  SUM(s.cogs) AS total_cogs,
  SUM(s.revenue - s.cogs) AS gross_profit,
  (SUM(s.revenue - s.cogs) / SUM(s.revenue)) * 100 AS gross_margin_pct,
  COUNT(DISTINCT s.product_id) AS product_count
FROM {{dataset}}.fct_sales s
JOIN {{dataset}}.dim_product p ON p.product_id = s.product_id
WHERE s.tenant_id = '{{tenant_id}}'
  AND s.order_date BETWEEN '{{start_date}}' AND '{{end_date}}'
  {% if category_filter %}
  AND p.category IN ({{category_filter}})
  {% endif %}
  AND s.revenue > 0  -- Avoid division by zero
GROUP BY 1
HAVING SUM(s.revenue) > 0  -- Filter out categories with no revenue
ORDER BY 5 DESC  -- Order by margin percentage descending
LIMIT {{row_limit}};

