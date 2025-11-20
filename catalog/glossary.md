---
noteId: "c0833210c5a311f0ac47819087bbe0ed"
tags: []

---

# Business Glossary
# Maps business terms to database schema (tables/columns), units, constraints, and synonyms
# Used for NL→SQL grounding and disambiguation

## Version
- **Version**: 1.0
- **Last Updated**: 2025-01-01
- **Owner**: Data Analyst / Solutions Architect
- **Review Date**: 2025-04-01

## Revenue & Sales Terms

### Net Sales
- **Definition**: Gross sales minus returns, discounts, and allowances
- **Table**: `fct_sales`
- **Column**: `net_sales` (calculated: `gross_sales - returns - discounts`)
- **Unit**: Currency (USD)
- **Synonyms**: revenue, net revenue, sales, net sales revenue
- **Constraints**: 
  - Must filter by `order_date` (date range required)
  - Must include `tenant_id` filter
  - Default time range: last 30 days if unspecified

### Gross Sales
- **Definition**: Total sales before deductions
- **Table**: `fct_sales`
- **Column**: `gross_sales`
- **Unit**: Currency (USD)
- **Synonyms**: total sales, gross revenue, sales before returns

### Returns
- **Definition**: Customer returns and refunds
- **Table**: `fct_sales`
- **Column**: `returns`
- **Unit**: Currency (USD)
- **Synonyms**: refunds, returns amount, returned merchandise

## Profitability Terms

### Gross Margin
- **Definition**: (Revenue - COGS) / Revenue * 100
- **Table**: Calculated from `fct_sales` and `fct_costs`
- **Formula**: `(SUM(revenue - cogs) / SUM(revenue)) * 100`
- **Unit**: Percentage
- **Synonyms**: margin, gross profit margin, margin percentage
- **Constraints**: Requires date range filter

### Margin by Category
- **Definition**: Gross margin broken down by product category
- **Table**: `fct_sales` JOIN `dim_product`
- **Grouping**: `dim_product.category`
- **Synonyms**: category margin, profitability by category

## Inventory Terms

### Inventory Turnover
- **Definition**: COGS / Average Inventory Value
- **Table**: `fct_inventory`, `fct_costs`
- **Formula**: `SUM(cogs) / AVG(inventory_value)`
- **Unit**: Ratio (times per period)
- **Synonyms**: stock turnover, inventory velocity, turnover ratio
- **Constraints**: Requires date range; typically calculated monthly or quarterly

### Average Inventory Value
- **Definition**: Mean inventory value over a period
- **Table**: `fct_inventory`
- **Column**: `inventory_value`
- **Unit**: Currency (USD)
- **Synonyms**: avg stock value, mean inventory

## Transaction Terms

### Average Ticket / AOV
- **Definition**: Average order value (total sales / transaction count)
- **Table**: `fct_transactions`
- **Formula**: `SUM(total_amount) / COUNT(DISTINCT transaction_id)`
- **Unit**: Currency (USD)
- **Synonyms**: average order value, AOV, average transaction value, ticket size
- **Constraints**: Requires date range filter

### Transaction
- **Definition**: A single customer purchase event
- **Table**: `fct_transactions`
- **Column**: `transaction_id`
- **Synonyms**: order, purchase, sale

## Time Dimensions

### Order Date
- **Table**: `fct_sales`, `fct_transactions`
- **Column**: `order_date`
- **Type**: DATE
- **Synonyms**: transaction date, sale date, purchase date
- **Constraints**: 
  - Required filter for most queries
  - Default range: last 30 days if unspecified
  - Max range: 365 days (policy enforced)

### Quarter / Q3
- **Definition**: Calendar quarter (Q1: Jan-Mar, Q2: Apr-Jun, Q3: Jul-Sep, Q4: Oct-Dec)
- **Synonyms**: Q1, Q2, Q3, Q4, quarter, quarterly

## Geographic Dimensions

### Store
- **Table**: `dim_store`
- **Column**: `store_id`, `store_name`
- **Synonyms**: location, retail location, branch

### Region
- **Table**: `dim_store`
- **Column**: `region`
- **Synonyms**: geographic region, territory, market

## Product Dimensions

### Category
- **Table**: `dim_product`
- **Column**: `category`
- **Synonyms**: product category, merchandise category

### Product
- **Table**: `dim_product`
- **Column**: `product_id`, `product_name`
- **Synonyms**: SKU, item, merchandise

## Channel Dimensions

### Channel
- **Table**: `fct_transactions`
- **Column**: `channel`
- **Values**: ["online", "in-store", "mobile", "call-center"]
- **Synonyms**: sales channel, purchase channel

## Ambiguity Notes

### Terms requiring disambiguation
- **"margin"**: Could mean gross margin %, margin $, or operating margin
  - Default: gross margin % if "percentage" mentioned
  - Default: margin $ if "dollars" or currency mentioned
  - Clarification question: "Do you mean margin percentage or margin dollars?"

- **"sales"**: Could mean gross sales or net sales
  - Default: net sales (gross - returns)
  - Clarification if ambiguous context

- **"ticket"**: Could mean transaction ticket or support ticket
  - Default: transaction (average ticket = AOV)
  - Context: if "support" nearby → support ticket

## Unit Conventions
- **Currency**: USD, displayed with $ prefix
- **Percentages**: Displayed as X.XX% (2 decimal places)
- **Ratios**: Displayed as X.XX (2 decimal places)
- **Dates**: ISO format (YYYY-MM-DD) or user locale

## Versioning & Governance
- Changes require approval from Data Analyst + Solutions Architect
- Semantic diffs tracked in catalog version history
- ACLs defined per tenant in `meta.yaml`

