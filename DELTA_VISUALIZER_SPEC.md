# Delta Visualization Notebook [Architecture & Interaction Specification (v1.0)]

# System Scope

## Directory Model

- Exactly one `delta` output directory per session.
- No cross-directory merging.
- No provenance tracking.
- No persistence across restarts.

A session is fully reset when the notebook restarts.

## Non-Goals (v1)

The system explicitly does not support:

- Automatic grouping by filename
- Language or command inference
- Cross-directory comparison
- Persisting groups or configuration
- Mixing memory dataset types in a group
- Statistical testing
- Implicit grouping logic

All grouping and comparison logic is user-defined.

# Core Architecture

The system consists of five layers:

1. Loader
2. Dataset Registry
3. Group Manager
4. Global Plot Configuration
5. Plot Engine

The UI (marimo) is strictly a frontend controller and does not contain domain logic.

# Data Model

## Dataset (Atomic Unit)

Each imported CSV becomes exactly one Dataset.

A Dataset contains:

- Unique internal identifier
- Source path
- User-editable display name
- Type (see below)
- Immutable reference to raw pandas DataFrame

Raw data is never modified.

## Dataset Types

Type is inferred from header validation.

### Time

Required columns:

- run_index
- duration_ns

### Memory Max

Required columns:

- run_index
- physical_bytes
- virtual_bytes

Must NOT contain:

- timestamp_ms

### Memory Timeline

Required columns:

- run_index
- timestamp_ms
- physical_bytes
- virtual_bytes

## Dataset Registry

The registry is flat and file-centric.

It contains:

- Mapping of dataset_id → Dataset

It does not contain groups or plot logic.

# Group Model

Groups are the primary plotting abstraction.

A Group contains:

- Unique identifier
- User-defined name
- List of dataset IDs
- Type inferred from first dataset

## Group Validation Rules

When adding a dataset to a group:

- Dataset must exist in registry.
- All datasets must share identical type.
- Mixing memory_max and memory_timeline is forbidden.
- Mixing time datasets with memory datasets is forbidden.

Validation failure must produce an explicit user-facing error.

# Global Plot Configuration

All plots are controlled by a single configuration object.

The configuration contains:

- Duration unit: ns | ms | s
- Y-axis scale: linear | log
- Memory metric: physical | virtual
- Timeline alignment strategy:
  - truncate
  - interpolate
  - per_run

- Palette mapping: dataset_id → color
- Label overrides: dataset_id → display label

No per-plot overrides are supported in v1.

# Data Transformation Rules

- raw_df is immutable.
- All unit conversions occur on temporary copies.
- No CSV modification.
- No transformed data persistence.
- All transformations are local to plotting functions.

# Plot Engine Contract

Plot functions must be pure.

Contract:

- Input: Group, PlotConfig
- Output: matplotlib Figure

Guarantees:

- No filesystem interaction
- No global state mutation
- Deterministic output
- No hidden side effects

Saving figures is handled outside the plot engine.

# Plot Behavior by Dataset Type

## Time

Input column: duration_ns

Behavior:

- Convert unit based on configuration.
- Produce boxplot.
- One box per dataset.
- Apply configured Y-scale.

## Memory Max

Input columns:

- physical_bytes
- virtual_bytes

Behavior:

- Select metric from configuration.
- Convert bytes to MB.
- Produce boxplot.
- One box per dataset.

## Memory Timeline

Input columns:

- timestamp_ms
- physical_bytes
- virtual_bytes

Behavior:

- Select metric from configuration.
- Convert bytes to MB.
- Produce line plot.
- One line per dataset.

## Timeline Alignment

Alignment strategy is global and applies to all timeline plots.

truncate

- Use minimum length across runs.

interpolate

- Interpolate onto shared time grid.

per_run

- Plot each run independently.

# User Interaction Flow

## Step 1 - Directory Selection

User selects one valid `delta` output directory.

Expected structure:

- output/
  - memory/
  - time/

## Step 2 - File Discovery

System scans recursively.

For each CSV:

- Validate header
- Classify dataset type
- Register Dataset (not grouped)

## Step 3 - Import Selection

User selects which discovered CSV files to load into the registry.

Partial loading is allowed.

## Step 4 - Manual Group Creation

User:

- Creates group
- Selects datasets
- Assigns name

Validation rules are enforced.

## Step 5 - Configure Global Settings

User sets:

- Duration unit
- Y-scale
- Memory metric
- Alignment strategy
- Palette
- Label overrides

## Step 6 - Plot

User selects group.

System generates figure via Plot Engine.

# Advanced Usage

The registry and groups are exposed to the notebook runtime.

Advanced users may directly access:

- registry.datasets[id].raw_df

The notebook acts as:

- Data provider
- Validation layer
- Plot abstraction layer

It does not restrict manual analysis.

# Architectural Principles

This design:

- Treats filenames as opaque
- Makes no semantic assumptions about commands
- Separates storage, grouping, configuration, and plotting
- Avoids implicit behavior
- Ensures deterministic plotting
- Enables future extension without structural change

If you want, next we can:

- Compress this further into a 2–3 page “Contributor Quick Spec”
- Or formalize the single in-memory AppState container design
- Or define error-handling philosophy and failure modes in the same slim style
