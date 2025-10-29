# Flet Charts Controls

Flet offers several controls for data visualization, allowing you to create interactive applications with various types of charts. You can use both built-in chart controls and integrate popular Python libraries like Matplotlib and Plotly.

### Built-in Chart Controls

Flet includes a set of native chart controls that are easy to use and are based on the `fl_chart` library. These controls are often more performant and offer better interactivity and animation compared to library-based solutions.

The primary built-in chart controls are:
*   **`LineChart`**: For drawing line charts.
*   **`BarChart`**: For drawing bar charts.
*   **`PieChart`**: For drawing pie charts.

These controls are a good starting point for most common charting needs and are designed to work seamlessly within the Flet ecosystem.

### Library-Based Chart Controls

For more complex or specialized visualizations, Flet provides controls to embed charts from powerful Python data visualization libraries.

*   **`MatplotlibChart`**: This control allows you to display any chart created with the Matplotlib library directly in your Flet application. You create a Matplotlib figure and then pass it to the `MatplotlibChart` control. This is useful for a wide range of plots, including heatmaps, contour plots, and complex multi-plot figures.
*   **`PlotlyChart`**: Similarly, this control lets you embed charts from the Plotly library, which is known for its highly interactive, publication-quality graphs.

### How to Use `MatplotlibChart`

Here is a basic example of how to use the `MatplotlibChart` control:

1.  **Install necessary libraries**:
    ```bash
    pip install flet matplotlib pandas
    ```

2.  **Create the Flet app**:
    You will need to import the required modules, create a Matplotlib figure, plot your data, and then wrap the figure in a `MatplotlibChart` control to add it to your page.

    ```python
    import flet as ft
    from flet.matplotlib_chart import MatplotlibChart
    import matplotlib.pyplot as plt
    import numpy as np

    def main(page: ft.Page):
        page.title = "Flet MatplotlibChart Example"

        # Create a Matplotlib figure
        fig, ax = plt.subplots()
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y)
        ax.set_title("Simple Sine Wave")
        ax.grid(True)

        # Wrap the figure in a MatplotlibChart control
        chart = MatplotlibChart(fig, expand=True)

        # Add the chart to the page
        page.add(chart)

    ft.app(target=main)
    ```

### Key Properties of `MatplotlibChart`

*   `figure`: The Matplotlib figure object to be displayed.
*   `isolated`: A boolean that, when set to `True`, prevents the chart from being redrawn on every page update, which can improve performance for complex charts. You would then need to call the chart's `update()` method manually.
*   `transparent`: Set to `True` to make the chart's background transparent.
*   `original_size`: If `True`, the chart is displayed in its original size instead of fitting into the available space.
