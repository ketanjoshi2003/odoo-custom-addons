# Retail Shop — Odoo 19 Module

A retail shop management module built from scratch for Odoo 19. It handles products, stock, sales and profit in one place, with business rules enforced in Python and an append-only stock movement ledger that records every stock-in, sale and restock. UI views include kanban, list, form, graph, pivot and calendar.

> Author: Ketan Joshi · Framework: Odoo 19 · License: LGPL-3

---

## The problem it solves

A small retail shop needs to answer four questions:

1. What products do I sell, and at what cost/price?
2. How much stock do I have, and how much of it is already sold?
3. What did I sell, and how much revenue did it generate after discounts?
4. How much profit did each sale make?

This module models that whole flow as six linked Odoo models with a sale state workflow, automatic calculations, and a movement ledger that makes every stock change auditable.

---

## Features

### Products (`retail.product`)
- Name, SKU (unique), sale price, cost price, image, active flag.
- **Computed `available_quantity`** = sum of the signed quantities in all `retail.stock.move` rows (stored, recalculated from the ledger).
- `move_ids` One2many gives direct access to the product's movement history.

### Stock (`retail.stock`)
- Stock entries linked to a product with quantity, price and date/time.
- Creating a stock entry automatically creates an `in` movement of `+quantity`, using a batched `@api.model_create_multi` override.
- Image shown via a `related` field from the product.
- Validation: quantity > 0, price ≥ 0.

### Stock movements (`retail.stock.move`)
- Append-only ledger: each row has a product, a signed quantity, a `move_type` (`in`, `out`, `return`), a date, and optional links to the source stock entry or sale.
- Ordered newest first (`date desc, id desc`).
- `available_quantity` is simply the sum of all rows — there is no separate stock counter to keep in sync.
- Own menu: **Retail Shop → Stock Movement** (kanban, list, form).

### Sales (`retail.sale`)
- Auto-numbered reference using an `ir.sequence` (`RS/2026/00001`).
- Customer (built-in `res.partner`), product, quantity, price and discount %.
- `@api.onchange('product_id')` fills in the sale price automatically.
- **Computed `total_amount`** = quantity × price − discount.
- State workflow: `Draft → Confirmed → Cancelled`, plus `Reset to Draft`, with form buttons for each transition.
- A `write()` override watches state changes and writes the ledger lines:
  - `draft → confirmed` → an `out` movement of `−quantity` (availability is checked **before** saving)
  - `confirmed → cancelled` → a `return` movement of `+quantity` (automatic restock)
  - all other transitions write no movement
- Tags via Many2many (`retail.sale.tag`) for labelling sales.
- Views: kanban, list, form, **graph, pivot and calendar**.

### Profit (`retail.profit`)
- One profit record per confirmed sale (enforced with a SQL `UNIQUE` constraint).
- **Computed `profit_amount`** = sale total − (quantity × product cost price).
- Validation: profit can only exist for a confirmed sale.

### Security
- `ir.model.access.csv` grants full CRUD on all six models to internal users (`base.group_user`).

---

## Odoo concepts demonstrated

| Concept | Where it appears |
|---|---|
| `@api.depends` computed fields | `total_amount`, `available_quantity`, `profit_amount` |
| Stored compute triggered by a One2many | `available_quantity` depends on `move_ids.quantity` |
| `@api.onchange` | price auto-fill on product selection |
| `@api.constrains` + `ValidationError` | discount range, prices, stock quantity, sale state |
| SQL constraints (Odoo 19 `models.Constraint`) | unique SKU, one profit per sale |
| `create()` override with `@api.model_create_multi` | sale numbers; batch-created `in` movements |
| `write()` override | reacting to sale state transitions; ledger lines |
| Batched multi-record create | list comprehension passed to `create([...])` in `stock.py` |
| Append-only ledger with signed quantities | `retail.stock.move` |
| State workflow + action methods | `action_confirm`, `action_cancel`, `action_reset_to_draft` |
| `ir.sequence` | automatic sale numbers |
| Relations | One2many, Many2one, Many2many, `related` field |
| View types | kanban, list, form, graph, pivot, calendar |
| Kanban field declarations | fields declared in `<kanban>` before the templates |
| XML data load order | `menus.xml` before `stock_move_view.xml` so the parent menu exists |
| Access rights | `ir.model.access.csv` |

---

## Installation

Place the module in your addons path and install it:

```bash
cd ~/workspace/odoo19
.venv/bin/python odoo-bin --addons-path=addons,../custom-addons -d odoo19 -i retail_shop
```

Use the virtualenv Python (`.venv/bin/python`) — the system Python does not have Odoo's dependencies installed.

If the module folder was added while Odoo was already running, update the module list first: **Apps → ⋮ → Update Modules List**.

To reload changes after editing XML/CSV:

```bash
.venv/bin/python odoo-bin --addons-path=addons,../custom-addons -d odoo19 -u retail_shop
```

Python changes additionally require restarting the Odoo process (or `--dev=reload`).

---

## How to use it

1. Open **Retail Shop → Products** and create a product with cost price, sale price and SKU.
2. Go to **Stock** and add a stock entry for that product (e.g. quantity 20). This writes an `in` movement.
3. Check the product form — `Available Quantity` should now show 20.
4. Go to **Sales** and create a sale. Pick the product, enter quantity and discount.
5. Click **Confirm**. An `out` movement of `−quantity` is written, so available quantity drops, and a sale number like `RS/2026/00001` is assigned.
6. Click **Cancel** on a confirmed sale. A `return` movement restores the quantity.
7. Go to **Profit** and create a profit record for a confirmed sale — the amount is computed automatically.
8. Open **Stock Movement** to see the full in/out/return history, and try the graph, pivot and calendar views on Sales for reporting.

**Things to try to see the validations work:**
- Enter a discount above 100 → a `ValidationError` is raised.
- Confirm a sale with quantity greater than available stock → blocked.
- Create a second profit record for the same sale → blocked by the unique constraint.
- Confirm then cancel a sale → watch two new rows appear in Stock Movement.

### Upgrading data created before the ledger
Stock entries and sales created **before** the ledger code was added have no movement rows, so their products will show 0 available. A one-time backfill is needed: create an `in` movement for each existing stock entry and an `out` movement for each currently-confirmed sale. Draft and cancelled sales need none (cancelled is net zero). The check by `stock_id` / `sale_id` makes the backfill safe to re-run.

---

## Project structure

```
retail_shop/
├── __manifest__.py              # dependencies, data files, metadata
├── data/
│   └── sale_sequence.xml        # ir.sequence for sale numbers (noupdate)
├── models/
│   ├── product.py               # product + ledger-based available quantity
│   ├── stock.py                 # stock entries + 'in' movement creation
│   ├── stock_move.py            # append-only movement ledger
│   ├── sale.py                  # sales, workflow, sequence, state-driven movements
│   ├── profit.py                # per-sale profit + constraints
│   └── tags.py                  # sale tags (Many2many)
├── security/
│   └── ir.model.access.csv      # CRUD rights for internal users
├── views/
│   ├── menus.xml                # root menu (loaded first)
│   ├── stock_move_view.xml      # movement ledger views + menu
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
- Why computed fields need correct `@api.depends`, and how a stored compute can be driven by an append-only ledger instead of being derived from several models.
- The difference between `create()` and `write()`: one runs at record birth, the other on every later edit.
- How `create()` works with `@api.model_create_multi`, and how to batch related records with `create([...])` instead of calling it in a loop.
- How to react to state transitions in `write()`, and why the availability check must happen before `super().write(vals)` while movement rows are created after it.
- Why both `old` and `new` states are needed to decide which ledger line (if any) to write.
- How Odoo validations work at three levels: Python `@api.constrains`, SQL `models.Constraint`, and workflow methods that raise `ValidationError`.
- How to expose the same data through many view types (kanban/list/form/graph/pivot/calendar) using `view_mode`.
- Why XML data files are loaded in manifest order (the parent menu must exist before a menuitem uses it) and why `noupdate="1"` protects sequence data on upgrades.
- Why kanban fields must be declared in the view before being used in a QWeb card template.

---

## Known limitations / next steps

- Editing or deleting a stock entry does not adjust the ledger yet. Planned: `write()`/`unlink()` on `retail.stock` plus an `adjustment` move type that writes compensating rows instead of changing history.
- The sale kanban is drag-enabled (`records_draggable="true"`), so a card can be dragged between columns without going through the buttons. Planned: a transition guard in `write()` and/or disabling dragging.
- Deleting a confirmed sale does not create a compensating `return` movement (if a profit record exists, deletion is blocked by `ondelete='restrict'`).
- Access rights are intentionally simple (full CRUD for all internal users); a production module would use dedicated security groups (e.g. manager vs. cashier).
- Automated tests are not included yet. Planned: `TransactionCase` tests for discount validation, insufficient-stock confirmation, ledger movements and profit computation.
- No QWeb report or customer-facing document is generated from a sale.
