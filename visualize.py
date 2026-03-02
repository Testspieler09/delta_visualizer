import marimo

__generated_with = "0.20.2"
app = marimo.App(
    width="columns",
    app_title="Visualize delta results",
    layout_file="layouts/visualize.slides.json",
)

with app.setup(hide_code=True):
    import marimo as mo
    import uuid

    # Custom from within the project
    from helper.core_models import DatasetRegistry, PlotConfig, AppState
    from helper.discovery import load_dataset
    from helper.grouping import create_group

    from helper.plotting.plot_dispatcher import plot_group

    # CONSTS
    LABEL_IDENTIFIER = "Dataset name"
    DEFAULT_LOADING_CALLOUT = mo.callout(
        "Nothing submitted yet",
        kind="info",
    )
    DEFAULT_GROUP_CREATION_CALLOUT = mo.callout(
        "So far no issues creating the groups",
        kind="info",
    )

    # Some global states
    groups, set_groups = mo.state({})

    loading_warnings = []
    loading_callout, set_loading_callout = mo.state(DEFAULT_LOADING_CALLOUT)
    group_creation_warnings = []
    group_creation_callout, set_group_creation_callout = mo.state(
        DEFAULT_GROUP_CREATION_CALLOUT
    )

    registry, set_registry = mo.state(DatasetRegistry())
    plot_config = None


@app.cell(hide_code=True)
def _(dataset_table_input, groups_mgmt_table, handle_create_group):
    # NOTE: All static (data needed already known at this point) UI elements get defined here
    csv_file_browser = mo.ui.file_browser(
        label="Select the benchmarks you want to compare",
        filetypes=["csv"],
        selection_mode="file",
        multiple=True,
    ).form(on_change=handle_csv_loading)

    clear_btn = mo.ui.button(
        label="Clear all", on_click=lambda _: set_groups({}), kind="danger"
    )

    delete_btn = mo.ui.button(
        label="Delete selected",
        on_click=lambda _: set_groups(
            {
                k: v
                for k, v in groups().items()
                if k not in {row["ID"] for row in (groups_mgmt_table.value or [])}
            }
        ),
        kind="neutral",
    )

    group_name_input = mo.ui.text(label="Groupname")

    creation_section = (
        mo.md("{name}\n{datasets}")
        .batch(name=group_name_input, datasets=dataset_table_input)
        .form(
            submit_button_label="Add Group to List",
            on_change=handle_create_group,
            bordered=True,
        )
    )

    config_form = (
        mo.md("""
        {memory_metric}

        {memory_unit}

        {timeline_alignment}

        {y_scale}

        {save_dir}
        """)
        .batch(
            memory_metric=mo.ui.dropdown(
                label="Memory metric",
                options=["physical", "virtual"],
                value="physical",
            ),
            memory_unit=mo.ui.dropdown(
                label="Memory unit", options=["mb", "bytes"], value="mb"
            ),
            timeline_alignment=mo.ui.dropdown(
                label="Timeline alignment",
                options=["truncate", "interpolate", "per_run"],
                value="truncate",
            ),
            y_scale=mo.ui.dropdown(
                label="Y scale",
                options=["linear", "log"],
                value="linear",
            ),
            save_dir=mo.ui.file_browser(
                label="Select a directory to save the plots to (optional) [If none selected the plots will not get saved automatically]",
                multiple=False,
                selection_mode="directory",
            ),
        )
        .form(
            show_clear_button=True,
            bordered=True,
            submit_button_label="Set Configuration",
        )
    )
    return (
        clear_btn,
        config_form,
        creation_section,
        csv_file_browser,
        delete_btn,
    )


@app.cell(hide_code=True)
def _():
    options = {
        f"{ds.display_name} ({ds.type})": ds.id for ds in registry().datasets.values()
    }

    dataset_table_input = mo.ui.table(
        data=[{LABEL_IDENTIFIER: name} for name in options.keys()],
        selection="multi",
        label="Select datasets",
    )

    def handle_create_group(form_value):
        if not form_value or not form_value["name"]:
            return
        if any(g.name == form_value["name"] for g in groups().values()):
            return

        selected_names = [row[LABEL_IDENTIFIER] for row in form_value["datasets"]]
        selected_ids = [options[name] for name in selected_names]

        try:
            new_group = create_group(registry(), form_value["name"], selected_ids)
            group_id = getattr(new_group, "id", str(uuid.uuid4()))
            set_groups({**groups(), group_id: new_group})
        except ValueError as e:
            group_creation_warnings.append(e)

        if group_creation_warnings:
            group_creation_warning_str = (
                "The group could not be created:\n\n"
                + "\n".join(f"- {w}" for w in group_creation_warnings)
            )
            set_group_creation_callout(
                mo.callout(mo.plain_text(group_creation_warning_str), kind="warn")
            )
        else:
            set_group_creation_callout(DEFAULT_GROUP_CREATION_CALLOUT)

    return dataset_table_input, handle_create_group


@app.function(hide_code=True)
def handle_csv_loading(form_value):
    new_registry = DatasetRegistry()
    loading_warnings = []

    if not form_value or form_value[0].path == ():
        loading_warnings.append("No files selected.")
    else:
        for csv in form_value:
            try:
                ds = load_dataset(csv.path)
                new_registry.add(ds)
            except ValueError as e:
                loading_warnings.append(str(e))

        set_registry(new_registry)
        set_groups({})
    if loading_warnings:
        loading_warning_str = "CSV data could not be loaded:\n\n" + "\n".join(
            f"- {w}" for w in loading_warnings
        )
        set_loading_callout(mo.callout(mo.plain_text(loading_warning_str), kind="warn"))
    elif form_value:
        set_loading_callout(
            mo.callout(
                "Successfully loaded benchmark data",
                kind="success",
            )
        )
    else:
        set_loading_callout(DEFAULT_LOADING_CALLOUT)


@app.cell(hide_code=True)
def _():
    current_groups_list = [
        {"ID": g_id, "Name": g.name, "Datasets": len(g.dataset_ids)}
        for g_id, g in groups().items()
    ]

    groups_mgmt_table = mo.ui.table(
        data=current_groups_list, selection="multi", label="Existing Groups"
    )
    return (groups_mgmt_table,)


@app.cell(hide_code=True)
def _(config_form):
    config = None

    if config_form.value:
        # TODO: add the missing configuration options when the notebook structure allows it
        # for example impl see: 87df64d
        config = PlotConfig(
            memory_metric=config_form.value["memory_metric"],
            memory_unit=config_form.value["memory_unit"],
            timeline_alignment=config_form.value["timeline_alignment"],
            y_scale=config_form.value["y_scale"],
        )

    app_state = AppState(registry=registry(), groups=groups(), config=config)
    return (app_state,)


@app.cell(column=1, hide_code=True)
def _(
    clear_btn,
    config_form,
    creation_section,
    csv_file_browser,
    delete_btn,
    groups_mgmt_table,
):
    mo.vstack(
        [
            mo.md("### Load Benchdata"),
            csv_file_browser,
            loading_callout(),
            mo.md("### Create plot groups"),
            creation_section,
            group_creation_callout(),
            mo.md("---"),
            mo.md("### Manage Existing Groups"),
            groups_mgmt_table,
            mo.hstack([delete_btn, clear_btn], justify="start"),
            mo.md("---"),
            mo.md("### Set plot configuration"),
            config_form,
        ]
    )
    return


@app.cell(hide_code=True)
def _(app_state):
    mo.output.append(
        mo.md("""---
    ### Final Plots
    """)
    )

    try:
        app_state.is_valid()
        plots = app_state.plot_all()
        if len(plots) == 1:
            mo.output.append(plots)
        elif len(plots) > 1:
            mo.output.append(mo.carousel(plots))
        else:
            mo.output.append(mo.callout("Nothing to plot", kind="info"))
        AppState.close_all_plots(plots)
    except ValueError as e:
        mo.output.append(mo.callout(str(e), kind="warn"))
    return


if __name__ == "__main__":
    app.run()
