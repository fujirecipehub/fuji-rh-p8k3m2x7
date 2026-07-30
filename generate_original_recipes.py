import json
import random
import hashlib

with open(r"C:\Users\user\OneDrive\デスクトップ\Projects\fuji-recipe-app\recipes.json", "r", encoding="utf-8") as f:
    recipes = json.load(f)

# --- Original name generation based on settings characteristics ---

mood_words_warm = ["Golden Hour", "Amber Glow", "Sunset Drift", "Warm Breeze", "Honey Light",
    "Copper Tone", "Autumn Haze", "Desert Wind", "Fireside", "Sunlit"]
mood_words_cool = ["Arctic Blue", "Frost Veil", "Moonlit", "Ocean Mist", "Silver Rain",
    "Winter Dawn", "Ice Crystal", "Cool Shade", "Twilight Blue", "Glacier"]
mood_words_neutral = ["Urban Walk", "Daily Journal", "Street Diary", "Quiet Moments", "Everyday Scene",
    "Casual Frame", "Plain Sight", "Simple Light", "Soft Focus", "Natural Eye"]
mood_words_vivid = ["Electric Bloom", "Neon Garden", "Color Burst", "Vivid Dream", "Saturated Life",
    "Pop Canvas", "Bold Palette", "Chromatic", "Rainbow Edge", "Bright Side"]
mood_words_muted = ["Faded Memory", "Dusty Road", "Old Film", "Vintage Cafe", "Worn Pages",
    "Retro Fade", "Pastel Dusk", "Mellow Tone", "Quiet Color", "Soft Wash"]
mood_words_mono = ["Shadow Play", "Noir Street", "Grain & Grit", "Contrast Life", "B&W Journal",
    "Mono Drama", "Dark Room", "Silver Print", "Light & Dark", "Ink Sketch"]
mood_words_cinematic = ["Cinema Reel", "Film Noir", "Director's Cut", "Scene One", "Silver Screen",
    "Reel Life", "Motion Blur", "Frame by Frame", "Opening Shot", "Final Take"]

subject_words = ["Portrait", "Landscape", "Street", "Travel", "Nature", "City",
    "Snap", "Scene", "Light", "Mood", "Tone", "Vision", "Frame", "View", "Shot"]

def get_color_temp(settings):
    wb = settings.get("white_balance", "")
    red_shift = 0
    blue_shift = 0
    if "Red" in wb:
        try:
            r = wb.split("Red")[0].strip().split()[-1]
            red_shift = int(r.replace("+", "").replace(",", ""))
        except:
            pass
    if "Blue" in wb:
        try:
            b = wb.split("Blue")[0].strip().split()[-1]
            blue_shift = int(b.replace("+", "").replace(",", ""))
        except:
            pass
    return red_shift, blue_shift

def get_tone_character(settings):
    highlight = settings.get("highlight_tone", "0")
    shadow = settings.get("shadow_tone", "0")
    color_val = settings.get("color", "0")

    try:
        h = int(highlight.split("(")[0].strip())
    except:
        h = 0
    try:
        s = int(shadow.split("(")[0].strip())
    except:
        s = 0
    try:
        c = int(color_val.split("(")[0].strip())
    except:
        c = 0
    return h, s, c

def is_monochrome(settings):
    sim = settings.get("film_simulation", "").lower()
    return "mono" in sim or "acros" in sim

def generate_name(recipe, index):
    settings = recipe["settings"]
    sim = settings.get("film_simulation", "Unknown")
    gen = recipe.get("generation", "")

    seed = hashlib.md5(f"{index}-{sim}-{gen}".encode()).hexdigest()
    rng = random.Random(seed)

    if is_monochrome(settings):
        mood = rng.choice(mood_words_mono)
    elif "velvia" in sim.lower() or "vivid" in sim.lower():
        mood = rng.choice(mood_words_vivid)
    elif "eterna" in sim.lower():
        mood = rng.choice(mood_words_cinematic)
    elif "classic chrome" in sim.lower() or "classic neg" in sim.lower():
        mood = rng.choice(mood_words_muted)
    elif "nostalgic" in sim.lower():
        mood = rng.choice(mood_words_muted)
    else:
        red, blue = get_color_temp(settings)
        h, s, c = get_tone_character(settings)
        if red > 3:
            mood = rng.choice(mood_words_warm)
        elif blue > 3 or red < -3:
            mood = rng.choice(mood_words_cool)
        elif c > 1:
            mood = rng.choice(mood_words_vivid)
        elif c < -1:
            mood = rng.choice(mood_words_muted)
        else:
            mood = rng.choice(mood_words_neutral)

    subject = rng.choice(subject_words)

    return f"{mood} {subject}"

# --- AI Image Prompt Generation ---

sim_descriptions = {
    "provia": "natural and balanced colors, standard film look",
    "velvia": "highly saturated and vivid colors, deep contrast",
    "astia": "soft and smooth skin tones, gentle pastel colors",
    "classic chrome": "muted desaturated colors with warm shadows, documentary film look",
    "classic negative": "high contrast with unique color shifts, warm highlights cool shadows",
    "pro neg. hi": "high contrast portrait tones, controlled colors",
    "pro neg. std": "soft neutral tones, subtle color palette",
    "eterna": "cinematic low-saturation look, soft contrast, movie film style",
    "eterna bleach bypass": "high contrast desaturated cinematic look, metallic tones",
    "nostalgic negative": "amber-tinted nostalgic warm tones, high saturation warm colors",
    "reala ace": "ultra-natural true-to-life colors, faithful reproduction",
    "acros": "high contrast black and white with fine grain",
    "monochrome": "classic black and white with smooth tonal gradation",
}

def get_sim_desc(sim):
    sim_lower = sim.lower()
    for key, desc in sim_descriptions.items():
        if key in sim_lower:
            return desc
    return "natural photographic look"

def generate_prompt(recipe, name):
    settings = recipe["settings"]
    sim = settings.get("film_simulation", "")
    sim_desc = get_sim_desc(sim)

    h, s, c = get_tone_character(settings)
    red, blue = get_color_temp(settings)

    contrast_desc = ""
    if h > 1 and s > 1:
        contrast_desc = "high contrast, deep blacks and bright highlights"
    elif h < -1 and s < -1:
        contrast_desc = "low contrast, soft and flat tones"
    elif h > 1:
        contrast_desc = "compressed highlights with punchy look"
    elif s > 1:
        contrast_desc = "deep rich shadows"

    wb_desc = ""
    if red > 3:
        wb_desc = "warm golden color temperature"
    elif red < -3 or blue > 3:
        wb_desc = "cool blue color temperature"
    elif red > 0 and blue < 0:
        wb_desc = "slightly warm tones"

    grain = settings.get("grain_effect", "")
    grain_desc = ""
    if "strong" in grain.lower():
        grain_desc = "visible film grain texture"
    elif "weak" in grain.lower():
        grain_desc = "subtle film grain"

    is_mono = is_monochrome(settings)

    if is_mono:
        scene = random.choice(["a quiet city street with interesting shadows",
            "an old building with dramatic light",
            "a person walking alone on a rainy street",
            "tree branches against bright sky",
            "a cafe interior with window light"])
    else:
        scene = random.choice(["a tranquil street scene with soft natural light",
            "a cozy cafe with warm ambient lighting",
            "a scenic landscape at golden hour",
            "a quiet park with dappled sunlight",
            "a cityscape with atmospheric mood",
            "a portrait with soft bokeh background",
            "flowers in a garden with gentle morning light",
            "a coastal scene with calm ocean waves"])

    parts = [f"A beautiful photograph of {scene}"]
    parts.append(f"Color grading: {sim_desc}")
    if contrast_desc:
        parts.append(contrast_desc)
    if wb_desc:
        parts.append(wb_desc)
    if grain_desc:
        parts.append(grain_desc)
    parts.append("Shot on Fujifilm camera, photorealistic, high quality")

    return ". ".join(parts)

# --- Process all recipes ---

used_names = set()
new_recipes = []
prompts = []

for i, recipe in enumerate(recipes):
    name = generate_name(recipe, i)

    # Ensure uniqueness
    base_name = name
    counter = 2
    while name in used_names:
        name = f"{base_name} {counter}"
        counter += 1
    used_names.add(name)

    prompt = generate_prompt(recipe, name)

    new_recipe = {
        "title": name,
        "generation": recipe["generation"],
        "imageUrl": "",  # To be filled with AI-generated images
        "settings": recipe["settings"]
    }
    new_recipes.append(new_recipe)
    prompts.append({
        "index": i,
        "title": name,
        "film_simulation": recipe["settings"].get("film_simulation", ""),
        "generation": recipe["generation"],
        "prompt": prompt
    })

out_dir = r"C:\Users\user\OneDrive\デスクトップ\Projects\fuji-recipe-app-original"

with open(f"{out_dir}\\recipes.json", "w", encoding="utf-8") as f:
    json.dump(new_recipes, f, ensure_ascii=False, indent=2)

with open(f"{out_dir}\\image_prompts.json", "w", encoding="utf-8") as f:
    json.dump(prompts, f, ensure_ascii=False, indent=2)

print(f"Generated {len(new_recipes)} original recipes")
print(f"Generated {len(prompts)} image prompts")
print(f"\nSample names:")
for r in new_recipes[:10]:
    print(f"  {r['generation']:12s} | {r['title']}")
print(f"\nSample prompt:")
print(f"  {prompts[0]['prompt'][:200]}...")
