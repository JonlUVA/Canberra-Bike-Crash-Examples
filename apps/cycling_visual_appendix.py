def rainfall_distribution_over_period():
    fig = px.box(
        df_raw_data[df_raw_data['rainfall_amount_(millimetres)'] != 0],
        y='rainfall_amount_(millimetres)',
        points=False,
        log_y=True
    )
    print()
    return fig