# Retail Shop — Odoo 19 Module

A retail shop management module built from scratch for Odoo 19. It handles products, stock, sales and profit in one place, with business rules enforced in Python and a full set of UI views (kanban, list, form, graph, pivot and calendar).

> Author: Ketan Joshi · Framework: Odoo 19 · License: LGPL-3

---

## The problem it solves

A small retail shop needs to answer four questions:

1. What products do I sell, and at what cost/price?
2. How much stock do I have, and how much of it is already sold?
3. What did I sell, and how much revenue did it generate after discounts?
4. How much profit did each sale make?

This module models that whole flow as four linked Odoo models with a sale state workflow and automatic calculations.

---

## Features

### Products (`retail.product`)
- Name, SKU (unique), sale price, cost price, image, active flag.
- **Computed `available_quantity`** = total stock received − quantity in confirmed sales.
- Automatic recalculation when stock entries or sale states change.

### Stock (`retail.stock`)
- Stock entries linked to a product with quantity, price and date.
- Image shown via a `related` field from the product.
- Validation: quantity > 0, price ≥ 0.

### Sales (`retail.sale`)
- Auto-numbered reference using an `ir.sequence` (`RS/2026/00001`).
- Customer (built-in `res.partner`), product, quantity, price and discount %.
- `@api.onchange('product_id')` fills in the sale price automatically.
- **Computed `total_amount`** = quantity × price − discount.
- State workflow: `Draft → Confirmed → Cancelled`, with form buttons for each transition.
- `action_confirm()` blocks confirmation when there isn't enough stock.
- Tags via Many2many (`retail.sale.tag`) for labelling sales.
- Views: kanban, list, form, **graph, pivot and calendar**.

### Profit (`retail.profit`)
- One profit record per confirmed sale (enforced with a SQL `UNIQUE` constraint).
- **Computed `profit_amount`** = sale total − (quantity × product cost price).
- Validation: profit can only exist for a confirmed sale.

### Security
- `ir.model.access.csv` grants full CRUD on all five models to internal users (`base.group_user`).

---

## Odoo concepts demonstrated

| Concept | Where it appears |
|---|---|
| `@api.depends` computed fields | `total_amount`, `available_quantity`, `profit_amount` |
| `@api.onchange` | price auto-fill on product selection |
| `@api.constrains` + `ValidationError` | discount range, prices, stock quantity, sale state |
| SQL constraints (Odoo 19 `models.Constraint`) | unique SKU, one profit per sale |
| State workflow + action methods | `action_confirm`, `action_cancel`, `action_reset_to_draft` |
| `ir.sequence` + `create()` override | automatic sale numbers (`@api.model_create_multi`) |
| Relations | One2many, Many2one, Many2many, `related` field |
| View types | kanban, list, form, graph, pivot, calendar |
| Business logic in the ORM | stock availability check on confirmation |
| Access rights | `ir.model.access.csv` |

---

## Installation

Place the module in your addons path and install it:

```bash
cd ~/workspace/odoo19
./odoo-bin --addons-path=addons,../custom-addons -d odoo19 -i retail_shop
```

If the module folder was added while Odoo was already running, update the module list first: **Apps → ⋮ → Update Modules List**.

To reload changes after editing XML/CSV:

```bash
./odoo-bin --addons-path=addons,../custom-addons -d odoo19 -u retail_shop
```

Python changes additionally require restarting the Odoo process (or `--dev=reload`).

---

## How to use it

1. Open **Retail Shop → Products** and create a product with cost price, sale price and SKU.
2. Go to **Stock** and add a stock entry for that product (e.g. quantity 20).
3. Check the product form — `Available Quantity` should now show 20.
4. Go to **Sales** and create a sale. Pick the product, enter quantity and discount.
5. Click **Confirm**. The available quantity drops by the sold amount, and a sale number like `RS/2026/00001` is assigned.
6. Go to **Profit** and create a profit record for that sale — the amount is computed automatically.
7. Try the graph, pivot and calendar views on Sales for reporting.

**Things to try to see the validations work:**
- Enter a discount above 100 → a `ValidationError` is raised.
- Confirm a sale with quantity greater than available stock → blocked.
- Create a second profit record for the same sale → blocked by the unique constraint.

---

## Project structure

```
retail_shop/
├── __manifest__.py              # dependencies, data files, metadata
├── data/
│   └── sale_sequence.xml        # ir.sequence for sale numbers (noupdate)
├── models/
│   ├── product.py               # product + computed available quantity
│   ├── stock.py                 # stock entries + constraints
│   ├── sale.py                  # sales, workflow, sequence, computed totals
│   ├── profit.py                # per-sale profit + constraints
│   └── tags.py                  # sale tags (Many2many)
├── security/
│   └── ir.model.access.csv      # CRUD rights for internal users
├── views/
│   ├── menus.xml                # root menu
│   ├── product_views.xml
│   ├── stock_views.xml
│   ├── sale_views.xml
│   ├── profit_views.xml
│   └── tags_view.xml
└── static/description/icon.png  # module icon
```

---

## What I learned building this

- How to design related models and choose between One2many / Many2one / Many2many.
- Why computed fields need correct `@api.depends`, and how stale values happen when a dependency is missing (fixed by adding `sale_ids` to `available_quantity`).
- How `create()` works with `@api.model_create_multi` and how to assign sequence numbers without breaking multi-record creation.
- How Odoo validations work at three levels: Python `@api.constrains`, SQL `models.Constraint`, and workflow methods that raise `ValidationError`.
- How to expose the same data through many view types (kanban/list/form/graph/pivot/calendar) using `view_mode`.
- How XML data files are loaded via the manifest and why `noupdate="1"` protects sequence data on upgrades.

---

## Known limitations / next steps

- Access rights are intentionally simple (full CRUD for all internal users); a production module would use dedicated security groups (e.g. manager vs. cashier).
- Cancelling a sale does not automatically restock its quantity — the computed `available_quantity` updates because it only counts confirmed sales, but there is no stock movement history.
- Automated tests are not included yet. Planned: `TransactionCase` tests for discount validation, insufficient-stock confirmation and profit computation.
- No QWeb report or customer-facing document is generated from a sale.
