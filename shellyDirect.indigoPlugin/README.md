# shellyDirect – Indigo plugin for Shelly devices

Controls and monitors Shelly Wi-Fi devices directly over your local network.
No Shelly cloud, no external MQTT broker and no extra Python modules are needed.

## What it does

- **Finds Shelly devices** on your network and creates the matching Indigo devices, with one child device per extra channel, phase or sensor.
- **Reads their status**: on/off, brightness, position, power, voltage, current, energy, temperature, humidity, battery, Wi-Fi signal, firmware and update status.
- **Switches and controls them** from Indigo: on, off, toggle, dim, position covers, set colors and thermostat values.
- **Gets changes right away** instead of only by polling:
  - **Gen1:** the device calls the plugin's built-in HTTP listener ("action URLs") whenever it switches or a button is pressed. It can also send its full status over MQTT.
  - **Gen2/3/4:** the plugin keeps a websocket open to each device. Alternatively, the device can send its updates to the plugin's built-in MQTT broker.
- **Polls as a backup:** when a device reports changes itself, polling slows down to at most every 5 minutes.
- **Marks devices as expired** when they stop answering.
- **Keeps SQL Logger working:** every state is written with its declared type, and new devices start with typed values instead of blanks.

## Supported devices

### Gen1

| Indigo device type | Shelly models |
|---|---|
| shelly1, shelly1pm, shelly1l | Shelly 1, 1PM, 1L |
| shellyswitch25 (+ child), shellyswitch25-roller | Shelly 2.5 (relay and roller mode), Shelly 2, UNI |
| shelly4pro (+ child) | Shelly 4Pro |
| shellyplug, shellyplug-s | Plug, Plug E, Plug S, Plug US |
| shellyix3 (+ child) | i3 |
| shellybutton1 | Button 1, Button 2 |
| shellydimmer, shellydimmer2 | Dimmer 1, Dimmer 2 |
| shellyrgbw2, shellybulb, ShellyBulbDuo, ShellyVintage | RGBW2, Bulb / Color Bulb, Duo, Vintage |
| shellyem (+ child), shellyem3 (+ child) | EM, 3EM |
| shellyht (+ child) | H&T |
| shellyflood, shellysmoke, shellygas | Flood, Smoke, Gas |
| shellymotionsensor | Motion, Motion 2 |
| shellydw | Door/Window 1 and 2 |
| shellytrv (+ child) | TRV thermostat |
| ext_temperature, ext_humidity | sensors on the add-on of a Shelly 1 / 1PM |

### Gen2 / Gen3 / Gen4

The device type is chosen from the parts (components) the device reports, not from its model name. A new model made of the same parts is supported automatically.

| Indigo device type | Shelly models | Shown in Indigo as |
|---|---|---|
| shellygen2switch (+ child) | Plus 1 / 1PM / 2PM, Plus Plug S, 1 / 1PM / 2PM Gen3, Pro 1 / 2 / 3 / 4PM, Mini, Wall Display, Plus UNI | relay, with power meter where available |
| shellygen2cover (+ child) | Plus 2PM in cover mode, 2PM Gen3, Pro Dual Cover | dimmer: brightness = position (0 closed … 100 open), on = open, off = close |
| shellygen2light (+ child) | Plus Wall Dimmer, Dimmer Gen3, Pro Dimmer, Plus RGBW PM in light mode | dimmer |
| shellygen2rgbw | Plus RGBW PM in RGB / RGBW mode | color dimmer |
| shellygen2input (+ child) | Plus i4, i4 Gen3 | sensor: on/off in switch mode; `lastEvent` (single_push, double_push, long_push …) in button mode |
| shellygen2pm | Plus PM Mini, PM Mini Gen3 | power meter |
| shellypro3em (+ child) | Pro 3EM (incl. 3×120 A), 3EM-63 Gen3, EM Gen3, Pro EM-50 | totals on the parent; phases A/B/C, or channels 1–3 in single-phase mode, on the children |
| shellyplusht (+ child) | Plus H&T, H&T Gen3 | temperature on the parent, humidity on the child |
| shellygen2alarm | Plus Smoke, Flood Gen4 | sensor: on = alarm, plus mute and battery |

Plus one device type that is not a Shelly:

| Device type | What it does |
|---|---|
| shellySumMeters | **Sum of meters**: adds up power, current and energy states of up to 8 other devices each; see [Sum of meters](#sum-of-meters) |

Not supported: Bluetooth (BLU) devices, and the light sensor and voltmeter of the Wall Display and Plus UNI.

## Setup

1. **Install:** double-click `shellyDirect.indigoPlugin`. Indigo copies it to its plugin folder and enables it.
2. **Open the plugin config** (Plugins → shellyDirect → Configure…) and set:
   - **IP number of the Indigo server.** The devices use it to reach the plugin, for both action URLs and MQTT.
   - **IP port of the HTTP listener**, default 7980. Use a free port above 5000; the Gen1 action URLs point here.
   - **User ID / password / port of the Shelly devices:** leave empty with port 80 if you did not set a login on the devices. Gen2+ devices always use the user `admin` with this password.
   - **Shelly devices API version:** choose **2021**. All current Gen1 firmware needs it; with 2020 the action URLs are silently ignored.
   - **Folder** for new devices (optional).
3. **Gen2/3/4 options:**
   - **Subscribe via websocket:** on by default. You get instant updates from mains-powered Gen2+ devices with nothing to set up on the device.
   - **Update at most every … seconds:** limits how often fast changes, like power, are written to Indigo.
4. **Built-in MQTT broker (optional):** turn it on and set its port (default 1883) and, if you want, a user and password. Use it for:
   - battery devices that sleep (Plus H&T, Plus Smoke, Flood), which can't keep a websocket open;
   - Gen1 devices, if you want their full status every 30 seconds without polling.
   The broker only receives messages, and only from Shelly devices; it does not pass anything on.
5. **Other options:** temperature unit, number of digits shown, curl or Python requests, writing state changes to the Indigo log, SQL Logger handling, and debug areas.

## Connecting devices

### Find devices automatically

- **Plugins → shellyDirect → Start Shelly device discovery Process**: enter a range, or only the first IP number for one device.
- The plugin asks each IP number for its type, creates the device and its children, and pushes its settings (Gen1).
- A log line `created new device: name, type, ip#` confirms each one.
- **Battery devices only answer while awake.** Press their button during the scan, or let them connect over MQTT (below).
- **A device that changed its IP number** is recognized by its MAC address and moved to the new IP.

### Give the devices a fixed IP number

Use a DHCP reservation in your router, or a static IP in the device's own web page. The action URLs and polling use the IP number.

### Gen1: action URLs (instant updates)

- After creating a Gen1 device, the plugin writes the action URLs into it, e.g. `out_on_url`, `out_off_url`, `btn_on_url` → `http://<indigo-ip>:7980/?…`.
- **To push them again:** Plugins → shellyDirect → **Set on device: action URLs + settings (gen1)**.
- **To check them:** open `http://<device-ip>/settings/actions`; the `urls` must point to your Indigo IP and port.
- **If the device does not accept them,** the log shows a warning. Check the "Shelly devices api version" setting first.

### MQTT: point devices at the plugin

- **Plugins → shellyDirect → Set on device: MQTT server = plugin broker (gen1 + gen2):** pick one device, all Gen2 devices, or all devices.
- **What it sets:** MQTT on, the server set to the Indigo IP and broker port, and the broker user and password.
  - **Gen2:** also turns on "RPC status notifications".
  - **Gen1:** also sets a status message every 30 seconds.
- **Restart:** the device restarts if needed. Devices that are already set up are left alone.
- **Sleeping devices** are retried for 15 minutes; press their button to wake them.
- **Gen1: the Shelly cloud is switched off while MQTT is on.** The Shelly app then only works on your home Wi-Fi. Gen2+ devices keep the cloud.
- **Not needed:** "Enable RPC over MQTT". The plugin sends commands over HTTP.
- **Unknown devices:** a device that connects to the broker but has no Indigo device yet is probed and created like a scan would.

### Add a device by hand

Create a new Indigo device, choose type *shellyDirect* and the model, then enter the IP number and save. Child devices are created with the first status message.

## Configuring devices

Every device has an edit dialog (double-click the device in Indigo):

- **IP number / MAC:** change the MAC only when you swap the hardware.
- **Polling frequency:** fixed, or *automatic adaptive*, the default. While the device reports changes itself over websocket, MQTT or action URLs, polling slows down.
- **Expiration:** how long without contact before the device is marked `expired`. Battery devices default to 14 hours.
- **Device-specific settings** (Gen1), such as button type, default state and LED. These are pushed to the device when you save.
- **PRINT button:** writes all properties and states of the device, each with its value type, to the Indigo log. Useful for checking a device or a SQL Logger problem.

Device features that are not in the edit dialog (gas sensor, TRV, roller) are in the plugin menu; see [Menu items](#menu-items).

### Sum of meters

Adds up power, current (amps) and energy from other devices, for example all phases and channels of several energy meters.

1. Create a new Indigo device, type *shellyDirect*, model *Sum of meters*.
2. For power, current and energy, choose how many sources to add (0–8, default 1) and the unit of the sum. The device, state and unit menus appear for that many slots; a slot left without a device is skipped.
3. For each source, choose a device, one of its states and the unit that state is in. Any Indigo device with numeric states works, including devices of other plugins. The state menu shows each state's current value. When you pick a device, a state with a matching name (power, current/amp, energy) is preselected.
4. Choose which sum the device list shows, then save.

Units: power mW, W, kW; current mA, A; energy Ws (J), Wh, kWh, MWh. The defaults are the Shelly units: W, A and Wh. Each source value is converted to the unit of its sum. If a state name ends in a unit, such as `energy_kWh`, that unit is preselected.

States: `power1`…`power8`, `current1`…`current8` and `energy1`…`energy8` hold the source values, converted to the unit of the sum. `powerSum`, `currentSum` and `energySum` hold the totals. `source_Power`, `source_Current` and `source_Energy` list the source device ids in slot order, for example `1378652208, 51092918`, and `lastSumUpdate` is the time of the last change.

For each sum (`powerSum`, `currentSum`, `energySum`) there are daily statistics, for example for power:

| State | Meaning |
|---|---|
| `powerSumMinToday`, `powerSumMinTodayAt` | lowest value today and when |
| `powerSumMaxToday`, `powerSumMaxTodayAt` | highest value today and when |
| `powerSumAveToday` | time-weighted average since midnight: each value counts for as long as it lasted |
| `…Yesterday`, `…YesterdayAt` | the same for yesterday, moved over at midnight |

After a plugin restart, today's values continue from the states.

**Sum of sums:** a sum device can be a source of another sum device, for example phases → floor → building → site. Picking a sum device as a source preselects its `powerSum`, `currentSum` or `energySum` and its unit. A change goes up through all levels within moments. Saving refuses a loop, such as A adding up B while B adds up A, and the message shows the loop. Don't add the same meter both directly and through a lower-level sum, or it is counted twice.

The sums update as soon as a source state changes. If nothing has changed for 5 minutes, the device rereads all sources and writes its states anyway, including `lastSumUpdate`. A source that is missing or not a number counts as 0, and the plugin logs a warning once.

## Device states and actions

### States all devices have

| State | Meaning |
|---|---|
| `lastMessageFromDevice` | time of the last message or answer from the device |
| `expired` | `yes` when the device has not answered within its expiration time |
| `upFor` | time since the device last started |
| `lastStatusChange`, `lastOnOffChange` | time of the last change, and of the last on/off change |
| `action_from_device` | last event or action URL the device sent |
| `MAC`, `created`, `WiFi_rssi`, `cloud`, `software_update_available` | device info (shown on the parent device) |
| `model`, `firmware`, `wsSubscription`, `mqttConnection` | Gen2+ only: model, firmware version, websocket and MQTT connection status |

### States per kind of device

| Kind | States |
|---|---|
| Relays and plugs | `onOffState`, `power`, `energy`, `input`, `Temperature_internal`, `overtemperature` (Gen1), `overPower` (Gen1); Gen2+ also `voltage`, `current`, `powerFactor`, `frequency` |
| Gen1 inputs (relays, i3, Button) | `input`, `input_short`, `input_long`, `input_short_double` …, `event_cnt`, `lastEvent` |
| Energy meters | `power`, `voltage`, `current`, `energy`, `energyReturned`, `powerFactor`; Gen1 also `reactive`; Pro 3EM also `apparentPower`, `frequency`, plus `currentN` on the parent |
| Dimmers and color lights | `onOffState`, `brightnessLevel`, `redLevel` / `greenLevel` / `blueLevel` / `whiteLevel` (color models), `power`, `energy` |
| Covers / rollers | `brightnessLevel` = position, `onOffState` (open), `coverState` (Gen2+) or `state` (Gen1), `lastDirection`, `power` |
| Gen2+ inputs (i4) | `onOffState` and `input` (switch mode), `lastEvent` and `lastEventTime` (button mode), `analogPercent` |
| Temperature / humidity | `Temperature` or `Humidity`, with min/max for today and yesterday, `batteryVoltage` |
| Alarms | Flood / Smoke / Gas (Gen1): `Flood` / `Smoke` / `Alarm`, `lastAlarm`, `previousAlarm`; Gen2+ alarms: `onOffState` = alarm, `alarmType`, `mute`, `batteryLevel` |
| Motion, Door/Window | motion / tamper / vibration triggers with their last times, `lux`, `illumination`, `tilt`, `state` (open/close), `batteryVoltage` |
| TRV | `Temperature`, setpoint, `valvePosition`, `valveState` + `lastValveChange` (from the device's valve_open / valve_close actions), `window_open`, `schedule`, `schedule_profile`, `boost_minutes`, `batteryVoltage` |

Energy units: Gen1 devices report `energy` in Wmin, Gen2+ devices in Wh.

### Actions from Indigo

| Device | Turn on / off / toggle | Brightness: set, brighten, dim | Color | Other |
|---|---|---|---|---|
| Relays and plugs | yes | – | – | – |
| Dimmers | yes | yes | – | – |
| Color lights, bulbs | yes | yes | yes (Gen1 also white temperature) | – |
| Covers (Gen2+) | on = open, off = close | set position | – | – |
| Shelly 2.5 roller | on = open, off = close | set position | – | stop, calibrate, move for x seconds (menu) |
| TRV | – | – | – | target temperature, schedule, boost … (menu *Set on device: thermostat (TRV) values*) |
| Gas | – | – | – | self test, mute / unmute (menu) |

Sensors, energy meters, inputs and alarms are read-only. Every action is followed by an immediate status request, so Indigo shows the real result.

## Menu items

Plugins → shellyDirect:

| Menu item | What it does |
|---|---|
| Start Shelly device discovery Process | scans one IP number ("to" empty) or a range and creates the devices it finds |
| Request Status from Shelly Device | asks a device for its settings and status now |
| Set on device: MQTT server = plugin broker (gen1 + gen2) | sets MQTT on the device to the built-in broker |
| Set on device: action URLs + settings (gen1) | writes the action URLs and device settings to Gen1 devices again |
| Set on device: gas alarm (self test, mute) | Shelly Gas: start self test, mute or un-mute the current alarm |
| Set on device: thermostat (TRV) values | TRV: target temperature, schedule, boost … |
| Manage roller device (shelly-25 roller) | Shelly 2.5 in roller mode: go to position, move for xx secs, stop, start calibration |
| Print emeter data to logfile | energy meter data of a device |
| (Un) ignore IP numbers | stop or allow messages and device creation for an IP number |
| Print Shelly dev info to logfile | plugin-side info for one or all devices |
| Print help to logfile | short help |

## Troubleshooting

- **A switch or button press shows up late (Gen1):** the action URLs are missing. Check the API version setting, then run *Set on device: action URLs + settings (gen1)*.
- **A Gen2+ device updates only every few minutes:** check its `wsSubscription` state (websocket) or `mqttConnection` state. Battery devices need MQTT.
- **"Could not get time … no internet connection" in a Gen1 device's web page:** the page asks Shelly's cloud for a timezone list, and the cloud now refuses that request. The device itself is fine.
- **SQL Logger errors for a device:** reload the plugin, delete that device's `device_history_<id>` table, and let it be recreated.
- **Something else:** turn on the matching debug area in the plugin config. The log is in `…/Logs/com.karlwachs.shellyDirect/plugin.log`.

## Changelog

Changes per version are listed in [`Contents/changelist.txt`](Contents/changelist.txt), newest first.
