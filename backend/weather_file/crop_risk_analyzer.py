"""
Crop Weather Risk & Suggestion Analyzer
A simple, zero-dependency Python script to predict crop weather risks,
calculate risk scores, and generate easy-to-understand farm suggestions.
"""

import os
import sys
import csv
import json
import math
import ssl
import socket
import urllib.request
import urllib.parse
import urllib.error

# Constants
import gzip
import zipfile

CSV_FILE = "All-India District-wise Crop and Climate Dataset (19842017).csv"
CSV_FILE_GZ = CSV_FILE + ".gz"
CSV_FILE_ZIP = CSV_FILE + ".zip"
CACHE_FILE = 'crop_data_cache.json'

def open_dataset():
    """
    Opens the dataset in text mode, transparently handling a compressed
    version of the file so the repo can ship a GitHub-friendly file size.
    Supports (in order of preference):
      1. .csv.gz  (created with gzip, e.g. on Mac/Linux)
      2. .csv.zip (created with Windows' built-in "Send to > Compressed folder")
      3. plain .csv (uncompressed, local use)
    """
    if os.path.exists(CSV_FILE_GZ):
        return gzip.open(CSV_FILE_GZ, 'rt', encoding='utf-8', newline='')
    if os.path.exists(CSV_FILE_ZIP):
        zf = zipfile.ZipFile(CSV_FILE_ZIP, 'r')
        # Find the CSV inside the zip regardless of its exact internal name
        inner_names = [n for n in zf.namelist() if n.lower().endswith('.csv')]
        if not inner_names:
            print_error(f"No .csv file found inside '{CSV_FILE_ZIP}'.")
            sys.exit(1)
        import io
        raw = zf.read(inner_names[0])
        zf.close()
        return io.StringIO(raw.decode('utf-8'))
    if os.path.exists(CSV_FILE):
        return open(CSV_FILE, 'r', encoding='utf-8', newline='')
    print_error(f"Dataset file not found. Expected one of '{CSV_FILE_GZ}', '{CSV_FILE_ZIP}', or '{CSV_FILE}' in the current directory.")
    print_info("Please ensure the dataset file is placed in the same folder as this script.")
    sys.exit(1)

# ANSI Color Codes for beautiful terminal styling
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_CYAN = "\033[96m"

# Detect if the terminal output supports unicode symbols without error
def supports_unicode():
    try:
        encoding = (sys.stdout.encoding or 'ascii').lower()
        if 'utf' in encoding or encoding == 'cp65001':
            return True
        if os.name == 'nt':
            import ctypes
            if ctypes.windll.kernel32.GetConsoleOutputCP() == 65001:
                return True
    except Exception:
        pass
    return False

USE_UNICODE = supports_unicode()

# Safe Symbol Table
SYM_SUCCESS = "✔" if USE_UNICODE else "[OK]"
SYM_INFO = "ℹ" if USE_UNICODE else "[INFO]"
SYM_WARNING = "⚠" if USE_UNICODE else "[WARN]"
SYM_ERROR = "✘" if USE_UNICODE else "[ERR]"
SYM_BULLET = "•" if USE_UNICODE else "*"
SYM_DEG = "°" if USE_UNICODE else " "

# Suggestions Emojis
EMOJI_SUN = "🌞" if USE_UNICODE else "[HEAT]"
EMOJI_COLD = "❄️" if USE_UNICODE else "[COLD]"
EMOJI_OK = "🟢" if USE_UNICODE else "[OK]"
EMOJI_RAIN_LOW = "🍂" if USE_UNICODE else "[DRY]"
EMOJI_RAIN_HIGH = "🌧️" if USE_UNICODE else "[RAIN]"
EMOJI_DISEASE = "🦠" if USE_UNICODE else "[PEST]"
EMOJI_DRY = "🌵" if USE_UNICODE else "[DRY AIR]"
EMOJI_WIND = "💨" if USE_UNICODE else "[WIND]"
EMOJI_ARROW = "👉" if USE_UNICODE else "->"

def print_header(title):
    print(f"\n{COLOR_BOLD}{COLOR_CYAN}{'=' * 60}{COLOR_RESET}")
    print(f"{COLOR_BOLD}{COLOR_CYAN}  {title}{COLOR_RESET}")
    print(f"{COLOR_BOLD}{COLOR_CYAN}{'=' * 60}{COLOR_RESET}")

def print_success(message):
    print(f"{COLOR_GREEN}{SYM_SUCCESS} {message}{COLOR_RESET}")

def print_info(message):
    print(f"{COLOR_BLUE}{SYM_INFO} {message}{COLOR_RESET}")

def print_warning(message):
    print(f"{COLOR_YELLOW}{SYM_WARNING} {message}{COLOR_RESET}")

def print_error(message):
    print(f"{COLOR_RED}{SYM_ERROR} {message}{COLOR_RESET}")

def print_debug(message):
    if os.environ.get('CROP_DEBUG'):
        print(f"{COLOR_CYAN}[DEBUG] {message}{COLOR_RESET}")

def check_dataset_exists():
    """Checks if the dataset file (compressed or plain) is present in the workspace."""
    if not os.path.exists(CSV_FILE_GZ) and not os.path.exists(CSV_FILE_ZIP) and not os.path.exists(CSV_FILE):
        print_error(f"Dataset file not found. Expected one of '{CSV_FILE_GZ}', '{CSV_FILE_ZIP}', or '{CSV_FILE}' in the current directory.")
        print_info("Please ensure the dataset file is placed in the same folder as this script.")
        sys.exit(1)

def get_crop_hierarchy():
    """
    Loads or creates a cache of States, Districts, and Crops from the CSV.
    This enables fast validation and list suggestions.
    """
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass

    print_info("Initializing dataset cache (this runs only once)...")
    hierarchy = {}
    
    try:
        with open_dataset() as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                state = row['State Name'].strip().title()
                dist = row['Dist Name'].strip().title()
                crop = row['Crops'].strip().lower()
                
                if not state or not dist or not crop:
                    continue
                
                if state not in hierarchy:
                    hierarchy[state] = {}
                if dist not in hierarchy[state]:
                    hierarchy[state][dist] = set()
                hierarchy[state][dist].add(crop)
                
                count += 1
                if count % 50000 == 0:
                    print(f"  Processed {count} rows...", end="\r")
                    
        # Convert sets to sorted lists for JSON serialization
        serialized_hierarchy = {}
        for state, dists in hierarchy.items():
            serialized_hierarchy[state] = {}
            for dist, crops in dists.items():
                serialized_hierarchy[state][dist] = sorted(list(crops))
                
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(serialized_hierarchy, f, indent=2)
            
        print_success("Dataset cache initialized successfully!")
        return serialized_hierarchy
    except Exception as e:
        print_error(f"Error reading CSV file to build cache: {e}")
        sys.exit(1)

def load_historical_data(target_state, target_district, target_crop):
    """
    Searches the CSV line-by-line for crop ideals and district historical data.
    """
    target_state = target_state.strip().lower()
    target_district = target_district.strip().lower()
    target_crop = target_crop.strip().lower()
    
    crop_ideals = None
    historical_records = []
    
    print_info(f"Searching dataset for {target_crop.title()} records in {target_district.title()}...")
    
    with open_dataset() as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_crop = row['Crops'].strip().lower()
            row_state = row['State Name'].strip().lower()
            row_dist = row['Dist Name'].strip().lower()
            
            # Extract crop ideals from any row containing this crop (since they are constant)
            if crop_ideals is None and row_crop == target_crop:
                try:
                    crop_ideals = {
                        'crop': row['Crops'].strip().lower(),
                        'Tmin_Ideal': float(row['Tmin_Ideal']),
                        'Tmax_Ideal': float(row['Tmax_Ideal']),
                        'Rain_Ideal': float(row['Rain_Ideal (mm/day)_Ideal']),
                        'RH_Ideal': float(row['RH_Ideal (%)_Ideal']),
                        'WS2M_Ideal': float(row['WS2M_Ideal'])
                    }
                except (ValueError, KeyError):
                    pass
            
            # Match state, district, crop for historical records
            if row_crop == target_crop and row_state == target_state and row_dist == target_district:
                historical_records.append(row)
                
    return crop_ideals, historical_records

# ---------------------------------------------------------------------------
# Open-Meteo integration
# ---------------------------------------------------------------------------
# Open-Meteo (https://open-meteo.com) is a free, no-API-key weather service.
# We use two of its endpoints:
#   1. Geocoding API  - resolves a place name to latitude/longitude
#   2. Forecast API   - returns today's temperature/rain/wind/humidity for
#      a given latitude/longitude
#
# ---------------------------------------------------------------------------

_SSL_CONTEXT = None

def _get_ssl_context():
    """Builds (once) an SSL context, falling back to unverified only as a
    last resort so we can tell the user *that* happened."""
    global _SSL_CONTEXT
    if _SSL_CONTEXT is not None:
        return _SSL_CONTEXT
    try:
        _SSL_CONTEXT = ssl.create_default_context()
    except Exception:
        _SSL_CONTEXT = ssl._create_unverified_context()
    return _SSL_CONTEXT

def _open_meteo_get(url, timeout=10):
    """
    Shared HTTP GET helper for all Open-Meteo calls.
    Returns (data_dict_or_None, error_message_or_None) so callers can decide
    how to react, and so we always know *why* something failed.
    """
    req = urllib.request.Request(url, headers={'User-Agent': 'CropWeatherRiskAnalyzer/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_get_ssl_context()) as response:
            status = response.getcode()
            raw = response.read().decode('utf-8')
            if status != 200:
                return None, f"HTTP {status} from Open-Meteo: {raw[:200]}"
            try:
                return json.loads(raw), None
            except json.JSONDecodeError as e:
                return None, f"Open-Meteo returned non-JSON response: {e}"
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode('utf-8')[:200]
        except Exception:
            pass
        return None, f"HTTP {e.code} error from Open-Meteo ({e.reason}). {body}"
    except urllib.error.URLError as e:
        reason = e.reason
        if isinstance(reason, ssl.SSLError):
            return None, f"SSL certificate verification failed ({reason}). Your network/proxy may be intercepting HTTPS traffic."
        if isinstance(reason, socket.timeout):
            return None, "Connection to Open-Meteo timed out. Check your internet connection or firewall/proxy settings."
        if isinstance(reason, socket.gaierror):
            return None, f"Could not resolve api.open-meteo.com / geocoding-api.open-meteo.com ({reason}). DNS may be blocked."
        return None, f"Could not reach Open-Meteo: {reason}"
    except socket.timeout:
        return None, "Connection to Open-Meteo timed out."
    except Exception as e:
        return None, f"Unexpected error calling Open-Meteo: {type(e).__name__}: {e}"

def test_open_meteo_connection():
    """
    Standalone connectivity check. Run with:
        python crop_weather_analyzer.py --test-connection
    Prints a clear pass/fail for each Open-Meteo endpoint instead of letting
    a failure hide silently behind the manual-entry fallback.
    """
    print_header("OPEN-METEO CONNECTIVITY TEST")

    print_info("Testing Geocoding API (geocoding-api.open-meteo.com)...")
    geo_url = "https://geocoding-api.open-meteo.com/v1/search?name=Pune&count=1&language=en&format=json"
    data, err = _open_meteo_get(geo_url)
    if err:
        print_error(f"Geocoding API: FAILED - {err}")
    elif data and data.get('results'):
        r = data['results'][0]
        print_success(f"Geocoding API: OK - resolved 'Pune' to {r['latitude']:.4f}, {r['longitude']:.4f}")
    else:
        print_warning("Geocoding API: reachable but returned no results for 'Pune' (unexpected).")

    print_info("Testing Forecast API (api.open-meteo.com)...")
    fc_url = ("https://api.open-meteo.com/v1/forecast?latitude=18.5204&longitude=73.8567"
              "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max"
              "&current=relative_humidity_2m&timezone=auto")
    data, err = _open_meteo_get(fc_url)
    if err:
        print_error(f"Forecast API: FAILED - {err}")
    elif data and 'daily' in data:
        tmax = data['daily']['temperature_2m_max'][0]
        print_success(f"Forecast API: OK - Pune today's max temp = {tmax}{SYM_DEG}C")
    else:
        print_warning("Forecast API: reachable but response missing expected fields.")

    print_info("If either test failed, share the exact error text above with your network/IT team -")
    print_info("it tells you whether this is DNS, SSL/proxy interception, a timeout, or an HTTP error,")
    print_info("rather than the app just silently dropping to manual weather entry.")

def geocode_district(state, district):
    """
    Geocodes district and state to latitude/longitude using the Open-Meteo
    Geocoding API. Tries several query variants, since exact census district
    names in the dataset often don't match Open-Meteo's place database.
    """
    candidates = [
        f"{district}, {state}, India",
        f"{district} District, {state}, India",
        f"{district}, India",
        district,
    ]

    last_err = None
    for query in candidates:
        print_info(f"Geocoding location: {query}...")
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(query)}&count=5&language=en&format=json"
        data, err = _open_meteo_get(url)
        print_debug(f"GET {url} -> err={err}")

        if err:
            last_err = err
            print_warning(f"Geocoding attempt '{query}' failed: {err}")
            continue

        results = data.get('results', [])
        if not results:
            print_debug(f"No results for query variant '{query}', trying next fallback...")
            continue

        # Prefer an explicit India match
        for result in results:
            if result.get('country', '').lower() == 'india':
                print_success(f"Location resolved: Lat {result['latitude']:.4f}, Lon {result['longitude']:.4f} (matched '{query}')")
                return float(result['latitude']), float(result['longitude'])

        # Otherwise take the first result
        print_success(f"Location resolved (first match, country unverified): Lat {results[0]['latitude']:.4f}, Lon {results[0]['longitude']:.4f}")
        return float(results[0]['latitude']), float(results[0]['longitude'])

    if last_err:
        print_error(f"Geocoding failed for all query variants. Last error: {last_err}")
    else:
        print_error(f"Geocoding API reachable, but no match found for '{district}, {state}' under any query variant tried.")
    return None

def fetch_current_weather(lat, lon):
    """
    Fetches the current weather parameters (today's max/min temp, rain sum,
    max wind speed, and current relative humidity) from Open-Meteo.
    """
    print_info("Fetching weather forecast from Open-Meteo...")
    url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
           f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max"
           f"&current=relative_humidity_2m&timezone=auto")

    data, err = _open_meteo_get(url)
    print_debug(f"GET {url} -> err={err}")

    if err:
        print_warning(f"Weather API failed: {err}")
        return None

    try:
        daily = data.get('daily', {})
        current = data.get('current', {})

        tmax = daily.get('temperature_2m_max', [None])[0]
        tmin = daily.get('temperature_2m_min', [None])[0]
        rain = daily.get('precipitation_sum', [None])[0]
        wind_speed = daily.get('wind_speed_10m_max', [None])[0]
        humidity = current.get('relative_humidity_2m')

        # Direct fallbacks
        if tmax is None: tmax = current.get('temperature_2m', 30.0)
        if tmin is None: tmin = current.get('temperature_2m', 20.0)
        if rain is None: rain = 0.0
        if wind_speed is None: wind_speed = current.get('wind_speed_10m', 10.0)  # km/h
        if humidity is None: humidity = 60.0

        # Convert wind speed from km/h to m/s to align with WS2M in dataset
        ws_mps = float(wind_speed) / 3.6

        return {
            'temp_max': float(tmax),
            'temp_min': float(tmin),
            'rain': float(rain),
            'humidity': float(humidity),
            'wind_speed': ws_mps
        }
    except Exception as e:
        print_warning(f"Weather API returned an unexpected response shape: {type(e).__name__}: {e}")
        return None

def calculate_risk(current, ideals, hist_avgs=None):
    """
    Calculates detailed risk scores (0-100%) for each parameter based on deviations.
    Also computes the overall weather impact risk score and category classification.
    """
    c_tmax = current['temp_max']
    c_tmin = current['temp_min']
    c_rain = current['rain']
    c_rh = current['humidity']
    c_ws = current['wind_speed']
    
    i_tmax = ideals['Tmax_Ideal']
    i_tmin = ideals['Tmin_Ideal']
    i_rain = ideals['Rain_Ideal']
    i_rh = ideals['RH_Ideal']
    i_ws = ideals['WS2M_Ideal']
    
    # 1. Temperature Max Risk (optimal range within 2 degrees, hazard beyond 8 degrees)
    tmax_diff = abs(c_tmax - i_tmax)
    tmax_risk = 0.0 if tmax_diff <= 2.0 else (100.0 if tmax_diff >= 8.0 else (tmax_diff - 2.0) / 6.0 * 100.0)
    
    # Temperature Min Risk
    tmin_diff = abs(c_tmin - i_tmin)
    tmin_risk = 0.0 if tmin_diff <= 2.0 else (100.0 if tmin_diff >= 8.0 else (tmin_diff - 2.0) / 6.0 * 100.0)
    
    temp_risk = (tmax_risk + tmin_risk) / 2.0
    
    # 2. Rainfall Risk
    if c_rain < 0.1:
        # Drought risk if crop wants high rain
        rain_risk = 60.0 if i_rain > 5.0 else 20.0
    else:
        # Flooding / Waterlogging risk
        if c_rain > i_rain * 3.0 and c_rain > 15.0:
            rain_risk = min(100.0, 50.0 + (c_rain / i_rain) * 10.0)
        # Inadequate rain risk
        elif c_rain < i_rain * 0.5:
            rain_risk = (1.0 - (c_rain / i_rain)) * 80.0
        else:
            rain_risk = 0.0
            
    # 3. Humidity Risk
    rh_diff = abs(c_rh - i_rh)
    if rh_diff <= 10.0:
        rh_risk = 0.0
    elif rh_diff >= 30.0 or c_rh > 90.0 or c_rh < 25.0:
        rh_risk = 100.0
    else:
        rh_risk = (rh_diff - 10.0) / 20.0 * 100.0
        
    # 4. Wind Risk
    if c_ws <= i_ws + 1.0:
        ws_risk = 0.0
    elif c_ws >= 8.0: # high winds threshold
        ws_risk = 100.0
    else:
        ws_risk = (c_ws - i_ws - 1.0) / (7.0 - i_ws) * 100.0
        ws_risk = min(100.0, max(0.0, ws_risk))
        
    # Overall Risk Score calculation (Weighted)
    # Temp Max & Min: 40%, Rain: 35%, Humidity: 15%, Wind: 10%
    overall_score = (temp_risk * 0.40) + (rain_risk * 0.35) + (rh_risk * 0.15) + (ws_risk * 0.10)
    
    # Category Prediction
    # Weather is Critical if overall risk is high or if major stress is extreme
    category = "Critical" if (overall_score >= 50.0 or temp_risk >= 80.0 or rain_risk >= 80.0) else "Ideal"
    
    return {
        'temp_risk': temp_risk,
        'tmax_risk': tmax_risk,
        'tmin_risk': tmin_risk,
        'rain_risk': rain_risk,
        'rh_risk': rh_risk,
        'ws_risk': ws_risk,
        'overall_score': overall_score,
        'category': category,
        # Standard Deviations as calculated in the dataset
        'dev_tmax': abs(c_tmax - i_tmax) / i_tmax,
        'dev_tmin': abs(c_tmin - i_tmin) / i_tmin,
        'dev_rain': abs(c_rain - i_rain) / i_rain if i_rain > 0 else 0,
        'dev_rh': abs(c_rh - i_rh) / i_rh,
        'dev_wind': abs(c_ws - i_ws) / i_ws
    }

def generate_suggestions(current, ideals, risks, crop_name):
    """
    Generates easy-to-understand agronomical suggestions for the farmer.
    """
    suggestions = []
    
    # 1. Temperature max advice
    if current['temp_max'] > ideals['Tmax_Ideal'] + 3.0:
        suggestions.append(
            f"{EMOJI_SUN} {COLOR_BOLD}Heat Alert:{COLOR_RESET} The temperature ({current['temp_max']:.1f}{SYM_DEG}C) is significantly higher than the ideal ({ideals['Tmax_Ideal']:.1f}{SYM_DEG}C) for {crop_name}.\n"
            f"   {EMOJI_ARROW} {COLOR_YELLOW}Advice:{COLOR_RESET} Water fields in the early morning or evening to cool the crop. Apply mulch to protect soil moisture."
        )
    elif current['temp_min'] < ideals['Tmin_Ideal'] - 3.0:
        suggestions.append(
            f"{EMOJI_COLD} {COLOR_BOLD}Cold Stress:{COLOR_RESET} The night temperature is dropping to {current['temp_min']:.1f}{SYM_DEG}C (Ideal: {ideals['Tmin_Ideal']:.1f}{SYM_DEG}C).\n"
            f"   {EMOJI_ARROW} {COLOR_YELLOW}Advice:{COLOR_RESET} Consider light evening watering (moist soil holds heat better) or using protective covers to prevent frost damage."
        )
    else:
        suggestions.append(f"{EMOJI_OK} {COLOR_BOLD}Temperature is optimal{COLOR_RESET} for {crop_name} development.")
        
    # 2. Rainfall advice
    if current['rain'] < 0.1:
        if ideals['Rain_Ideal'] > 4.0:
            suggestions.append(
                f"{EMOJI_RAIN_LOW} {COLOR_BOLD}Water Deficit:{COLOR_RESET} Dry weather detected, but {crop_name} ideally needs about {ideals['Rain_Ideal']:.1f} mm/day.\n"
                f"   {EMOJI_ARROW} {COLOR_YELLOW}Advice:{COLOR_RESET} Ensure active irrigation immediately. Water scarcity now can reduce grain/fruit yields drastically."
            )
        else:
            suggestions.append(f"{EMOJI_OK} {COLOR_BOLD}Dry weather is suitable{COLOR_RESET} for this crop phase; standard moisture is sufficient.")
    else:
        if current['rain'] > ideals['Rain_Ideal'] * 3.0 and current['rain'] > 15.0:
            suggestions.append(
                f"{EMOJI_RAIN_HIGH} {COLOR_BOLD}Excessive Rain:{COLOR_RESET} High rainfall ({current['rain']:.1f} mm) compared to ideal daily ({ideals['Rain_Ideal']:.1f} mm).\n"
                f"   {EMOJI_ARROW} {COLOR_YELLOW}Advice:{COLOR_RESET} Clear field drainage channels immediately to prevent waterlogging. Standing water rots roots and triggers disease."
            )
        elif current['rain'] < ideals['Rain_Ideal'] * 0.5:
            suggestions.append(
                f"{EMOJI_RAIN_LOW} {COLOR_BOLD}Inadequate Rain:{COLOR_RESET} Received {current['rain']:.1f} mm, which is below the crop's ideal requirement of {ideals['Rain_Ideal']:.1f} mm.\n"
                f"   {EMOJI_ARROW} {COLOR_YELLOW}Advice:{COLOR_RESET} Supplement with sprinkler irrigation if possible to maintain optimal soil moisture."
            )
        else:
            suggestions.append(f"{EMOJI_OK} {COLOR_BOLD}Rainfall is adequate{COLOR_RESET} and fits {crop_name}'s water requirements.")
            
    # 3. Humidity advice
    if current['humidity'] > ideals['RH_Ideal'] + 15.0 or current['humidity'] > 85.0:
        suggestions.append(
            f"{EMOJI_DISEASE} {COLOR_BOLD}High Disease Risk:{COLOR_RESET} Humidity is very high ({current['humidity']:.1f}%, Ideal: {ideals['RH_Ideal']:.1f}%).\n"
            f"   {EMOJI_ARROW} {COLOR_YELLOW}Advice:{COLOR_RESET} Damp conditions attract fungus, rust, and insect pests. Avoid overhead watering and inspect under the leaves for infection signs."
        )
    elif current['humidity'] < ideals['RH_Ideal'] - 20.0 or current['humidity'] < 35.0:
        suggestions.append(
            f"{EMOJI_DRY} {COLOR_BOLD}Dry Air Alert:{COLOR_RESET} Low humidity ({current['humidity']:.1f}%, Ideal: {ideals['RH_Ideal']:.1f}%).\n"
            f"   {EMOJI_ARROW} {COLOR_YELLOW}Advice:{COLOR_RESET} Transpiration rate is very high. Maintain proper soil dampness to prevent leaf drying."
        )
    else:
        suggestions.append(f"{EMOJI_OK} {COLOR_BOLD}Humidity is optimal{COLOR_RESET} ({current['humidity']:.1f}%) for pest prevention.")
        
    # 4. Wind speed advice
    if current['wind_speed'] > 6.0:
        suggestions.append(
            f"{EMOJI_WIND} {COLOR_BOLD}Strong Winds:{COLOR_RESET} Wind speed is {current['wind_speed']:.1f} m/s (Ideal: {ideals['WS2M_Ideal']:.1f} m/s).\n"
            f"   {EMOJI_ARROW} {COLOR_YELLOW}Advice:{COLOR_RESET} Do NOT spray pesticides or apply chemical powder fertilizers today, as they will drift away. Ensure taller plants are supported."
        )
        
    return suggestions

def print_dashboard(state, district, crop, current, ideals, risks, hist_records):
    """
    Renders a clean, structured command line dashboard representing the predictions.
    """
    print_header("CROP WEATHER RISK DASHBOARD")
    print(f"{COLOR_BOLD}Location:{COLOR_RESET} {district.title()}, {state.title()}  |  {COLOR_BOLD}Crop:{COLOR_RESET} {crop.title()}")
    
    # Historical metadata
    if hist_records:
        years = len(hist_records)
        yields = [float(r['YIELD (Kg per ha)']) for r in hist_records if r['YIELD (Kg per ha)']]
        avg_yield = sum(yields) / len(yields) if yields else 0.0
        
        crit_seasons = sum(1 for r in hist_records if r['Weather_Category'].strip().title() == 'Critical')
        pct_crit = (crit_seasons / years) * 100.0 if years > 0 else 0.0
        
        print(f"{COLOR_BOLD}Historical context (1984-2017):{COLOR_RESET} {years} seasons analyzed | Avg Yield: {avg_yield:.1f} Kg/ha")
        print(f"{COLOR_BOLD}Historical Climate Risk Rate:{COLOR_RESET} {pct_crit:.1f}% Critical weather seasons")
    else:
        print_warning("No district-specific historical yields found for this crop in our database. Using generalized crop model.")
        
    print(f"\n{COLOR_BOLD}CURRENT VS. IDEAL PARAMETERS:{COLOR_RESET}")
    print(f"{'-'*68}")
    print(f"{'Parameter':<22} | {'Current (Open-Meteo)':<20} | {'Crop Ideal (Dataset)':<20}")
    print(f"{'-'*68}")
    print(f"{'Max Temp':<22} | {current['temp_max']:>6.1f}{SYM_DEG}C            | {ideals['Tmax_Ideal']:>6.1f}{SYM_DEG}C")
    print(f"{'Min Temp':<22} | {current['temp_min']:>6.1f}{SYM_DEG}C            | {ideals['Tmin_Ideal']:>6.1f}{SYM_DEG}C")
    print(f"{'Daily Rain':<22} | {current['rain']:>6.1f} mm            | {ideals['Rain_Ideal']:>6.1f} mm/day")
    print(f"{'Humidity':<22} | {current['humidity']:>6.1f}%             | {ideals['RH_Ideal']:>6.1f}%")
    print(f"{'Wind Speed':<22} | {current['wind_speed']:>6.1f} m/s            | {ideals['WS2M_Ideal']:>6.1f} m/s")
    print(f"{'-'*68}")
    
    # Risk Score Panel
    score = risks['overall_score']
    if score < 25.0:
        score_color = COLOR_GREEN
        rating = "VERY LOW IMPACT RISK (Ideal)"
    elif score < 50.0:
        score_color = COLOR_YELLOW
        rating = "MODERATE IMPACT RISK"
    elif score < 75.0:
        score_color = COLOR_RED
        rating = "HIGH IMPACT RISK"
    else:
        score_color = COLOR_RED + COLOR_BOLD
        rating = "CRITICAL IMPACT RISK (Severe)"
        
    print(f"\n{COLOR_BOLD}WEATHER IMPACT PREDICTION:{COLOR_RESET}")
    print(f"  {SYM_BULLET} Predicted Weather Category: {COLOR_BOLD}{COLOR_RED if risks['category'] == 'Critical' else COLOR_GREEN}{risks['category'].upper()}{COLOR_RESET}")
    print(f"  {SYM_BULLET} Overall Weather Risk Score: {score_color}{score:.1f}%{COLOR_RESET} ({rating})")
    
    # Sub-component risks
    print(f"    - Temp Max Deviation Risk: {risks['tmax_risk']:.1f}%")
    print(f"    - Temp Min Deviation Risk: {risks['tmin_risk']:.1f}%")
    print(f"    - Rainfall Deviation Risk: {risks['rain_risk']:.1f}%")
    print(f"    - Humidity Deviation Risk: {risks['rh_risk']:.1f}%")
    print(f"    - Wind Speed Deviation Risk: {risks['ws_risk']:.1f}%")
    
    # Suggestions Panel
    print_header("FARMER SUGGESTIONS & GUIDANCE (EASY LANGUAGE)")
    suggestions = generate_suggestions(current, ideals, risks, crop.title())
    for suggestion in suggestions:
        print(suggestion)
        print()

def simulate_offline_weather():
    """
    Prompts user for manual weather inputs in case the API call fails or there's no internet.
    """
    print_warning("\nCould not fetch real-time weather from Open-Meteo.")
    print_info("Entering manual/simulated weather mode.")
    try:
        tmax = float(input("Enter Current Max Temperature (°C) [Default 30.0]: ") or 30.0)
        tmin = float(input("Enter Current Min Temperature (°C) [Default 20.0]: ") or 20.0)
        rain = float(input("Enter Daily Rain Sum (mm) [Default 0.0]: ") or 0.0)
        rh = float(input("Enter Relative Humidity (%) [Default 60.0]: ") or 60.0)
        ws = float(input("Enter Wind Speed (m/s) [Default 2.5]: ") or 2.5)
        
        return {
            'temp_max': tmax,
            'temp_min': tmin,
            'rain': rain,
            'humidity': rh,
            'wind_speed': ws
        }
    except Exception as e:
        print_error(f"Invalid input: {e}. Using standard weather baseline.")
        return {
            'temp_max': 30.0,
            'temp_min': 20.0,
            'rain': 0.0,
            'humidity': 60.0,
            'wind_speed': 2.5
        }

def run_interactive_cli():
    print_header("CROP WEATHER RISK & SUGGESTION ANALYZER")
    check_dataset_exists()
    hierarchy = get_crop_hierarchy()
    
    # 1. State Input
    states = sorted(list(hierarchy.keys()))
    print(f"\n{COLOR_BOLD}Step 1: Choose State{COLOR_RESET}")
    print(f"Available States in Dataset: {', '.join(states[:10])}... ({len(states)} total)")
    
    while True:
        state_input = input(f"{COLOR_BOLD}Enter State Name:{COLOR_RESET} ").strip().title()
        if state_input in hierarchy:
            state = state_input
            break
        else:
            # Try fuzzy match
            matches = [s for s in states if state_input.lower() in s.lower()]
            if len(matches) == 1:
                state = matches[0]
                print_success(f"Matched State: {state}")
                break
            elif len(matches) > 1:
                print_warning(f"Ambiguous input. Did you mean: {', '.join(matches)}?")
            else:
                print_error("State not found in dataset. Please check spelling or select from above.")
                
    # 2. District Input
    dists = sorted(list(hierarchy[state].keys()))
    print(f"\n{COLOR_BOLD}Step 2: Choose District in {state}{COLOR_RESET}")
    print(f"Available Districts: {', '.join(dists[:10])}... ({len(dists)} total)")
    
    while True:
        dist_input = input(f"{COLOR_BOLD}Enter District Name:{COLOR_RESET} ").strip().title()
        if dist_input in hierarchy[state]:
            district = dist_input
            break
        else:
            matches = [d for d in dists if dist_input.lower() in d.lower()]
            if len(matches) == 1:
                district = matches[0]
                print_success(f"Matched District: {district}")
                break
            elif len(matches) > 1:
                print_warning(f"Ambiguous input. Did you mean: {', '.join(matches)}?")
            else:
                print_error(f"District '{dist_input}' not found in {state}. Please select from above.")

    # 3. Crop Input
    crops = hierarchy[state][district]
    print(f"\n{COLOR_BOLD}Step 3: Choose Crop{COLOR_RESET}")
    print(f"Crops historically cultivated in {district}: {', '.join([c.title() for c in crops])}")
    
    while True:
        crop_input = input(f"{COLOR_BOLD}Enter Crop Name:{COLOR_RESET} ").strip().lower()
        if crop_input in crops:
            crop = crop_input
            break
        else:
            # Let them input any crop in the general dataset if they want, with warning
            all_crops = set()
            for s in hierarchy:
                for d in hierarchy[s]:
                    all_crops.update(hierarchy[s][d])
            
            if crop_input in all_crops:
                crop = crop_input
                print_warning(f"Crop '{crop.title()}' is not historically grown in {district}, but is in the dataset. Proceeding...")
                break
            else:
                matches = [c for c in crops if crop_input in c]
                if len(matches) == 1:
                    crop = matches[0]
                    print_success(f"Matched Crop: {crop.title()}")
                    break
                else:
                    print_error(f"Crop '{crop_input}' is not recognized in dataset. Please select from the list.")

    # 4. Fetch coordinates & weather
    coords = geocode_district(state, district)
    weather = None
    if coords:
        weather = fetch_current_weather(coords[0], coords[1])
        
    if not weather:
        weather = simulate_offline_weather()
        
    # 5. Load historical data
    ideals, historical_records = load_historical_data(state, district, crop)
    
    if not ideals:
        print_error(f"Could not load ideals for crop: {crop}. Make sure the dataset contains records of this crop.")
        sys.exit(1)
        
    # 6. Calculate risk and print dashboard
    risks = calculate_risk(weather, ideals, historical_records)
    print_dashboard(state, district, crop, weather, ideals, risks, historical_records)

if __name__ == "__main__":
    try:
        if len(sys.argv) >= 2 and sys.argv[1] == "--test-connection":
            test_open_meteo_connection()
            sys.exit(0)

        # Check command line args for non-interactive automation if needed
        if len(sys.argv) >= 4:
            state_arg = sys.argv[1]
            dist_arg = sys.argv[2]
            crop_arg = sys.argv[3]
            
            check_dataset_exists()
            ideals, historical = load_historical_data(state_arg, dist_arg, crop_arg)
            if not ideals:
                print_error(f"Crop ideals for '{crop_arg}' not found.")
                sys.exit(1)
                
            coords = geocode_district(state_arg, dist_arg)
            weather = None
            if coords:
                weather = fetch_current_weather(coords[0], coords[1])
            if not weather:
                # Standard weather fallback if offline in non-interactive mode
                weather = {
                    'temp_max': 31.0,
                    'temp_min': 21.0,
                    'rain': 0.0,
                    'humidity': 55.0,
                    'wind_speed': 2.2
                }
                print_info("Using offline standard weather fallback.")
                
            risks = calculate_risk(weather, ideals, historical)
            print_dashboard(state_arg, dist_arg, crop_arg, weather, ideals, risks, historical)
        else:
            run_interactive_cli()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
