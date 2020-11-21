# TVHeadend

This module provides a simple widget showing the status (idle or recording of your TVHeadend server) and the upcoming recordings.

## Demo

Here is a screenshot from my laptop showing the widget in the bar.

![Screenshot](images/tvh_widget.gif?raw=true)</br>

## Indicators

When the server is recording a red line will be shown under the icon. If there's an error, a yellow line will show above the icon (and check the logs).

## Installation

You can clone the repository and run:

```
python setup.py install
```
or, for Arch users, just copy the PKGBUILD file to your machine and build.

## Configuration

Add the code to your config (`~/.config/qtile/config.py`):

```python
from tvhwidget import TVHWidget
...
screens = [
    Screen(
        top=bar.Bar(
            [
                widget.CurrentLayout(),
                widget.GroupBox(),
                widget.Prompt(),
                widget.WindowName(),
                TVHWidget(),     
                widget.Clock(format='%Y-%m-%d %a %I:%M %p'),
                widget.QuickExit(),
            ],
            24,
        ),
    ),
]
```

## Customising

You may need to add the host address and login details via the "host" and "auth" keywords.

The widget can be customised with the following arguments:

<table>
	<tr>
		<td>refresh_interval</td>
		<td>Time to update data</td>
	</tr>
	<tr>
		<td>startup_delay</td>
		<td>Time before sending first web request</td>
	</tr>
	<tr>
		<td>host</td>
		<td>TVHeadend server address</td>
	</tr>
	<tr>
		<td>auth</td>
		<td>Auth details for accessing tvh. Can be None or tuple of (username, password)</td>
	</tr>
	<tr>
		<td>tvh_timeout</td>
		<td>Seconds before timeout for timeout request</td>
	</tr>
	<tr>
		<td>popup_format</td>
		<td>Upcoming recording text.</td>
	</tr>
	<tr>
		<td>popup_display_timeout</td>
		<td>Seconds to show recordings.</td>
	</tr>
	<tr>
		<td>warning_colour</td>
		<td>Highlight when there is an error.</td>
	</tr>
	<tr>
		<td>recording_colour</td>
		<td>Highlight when TVHeadend is recording</td>
	</tr>
</table>

## Contributing

If you've used this (great, and thank you) you will find bugs so please [file an issue](https://github.com/elParaguayo/qtile-widget-tvheadend/issues/new).
