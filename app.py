from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "FitGain AI Running!"


@app.route("/plan", methods=["POST", "OPTIONS"])
def plan():
    if request.method == "OPTIONS":
        return '', 200

    data = request.json

    age = int(data['age'])
    height = int(data['height'])
    current_weight = int(data['current_weight'])
    target_weight = int(data['target_weight'])
    months = int(data['months'])
    diet_type = data['diet_type']

    # ---------------- BMI ----------------
    height_m = height / 100
    bmi = current_weight / (height_m * height_m)
    target_bmi = target_weight / (height_m * height_m)

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal"
    else:
        category = "Overweight"

    # ---------------- BMR ----------------
    bmr = 10 * current_weight + 6.25 * height - 5 * age + 5
    maintenance = bmr * 1.55

    # ---------------- Goal ----------------
    weight_gain = max(0, target_weight - current_weight)

    if months == 0:
        months = 1

    days = months * 30

    # 🔥 Dynamic calorie surplus
    surplus = (weight_gain * 7700) / days
    surplus = min(700, max(150, surplus))

    total_calories = maintenance + surplus

    # ---------------- Macros ----------------
    protein = target_weight * 1.8
    fats = target_weight * 0.8
    carbs = max(0, (total_calories - (protein*4 + fats*9)) / 4)

    # ---------------- Strong Scaling ----------------
    weight_diff = target_weight - current_weight
    scale = 1 + (weight_diff / 15)
    scale = min(3, max(1, scale))

    # Protein foods
    eggs = int(2 * scale)
    milk = int(1 * scale)
    paneer = int(50 * scale + 50)

    # Carb foods
    banana = int(1 * scale + 1)
    roti = int(4 * scale)
    rice = int(1 * scale + 1)

    # Limits
    eggs = min(8, eggs)
    milk = min(4, milk)
    banana = min(6, banana)
    roti = min(10, roti)
    rice = min(4, rice)
    paneer = min(250, paneer)

    # ---------------- Plan Type ----------------
    if surplus > 500:
        plan_type = "🔥 Aggressive Gain"
    elif surplus > 300:
        plan_type = "⚡ Moderate Gain"
    else:
        plan_type = "💪 Lean Gain"

    # ---------------- Diet Logic (FIXED VEG/NON-VEG) ----------------
    if diet_type == "veg":
        breakfast = f"{paneer}g Paneer, {banana//2} Banana, 1 Glass Milk"
        dinner_protein = "Paneer"
        evening = "Peanut Butter Sandwich + Milk"
    else:
        breakfast = f"{eggs} Eggs, {banana//2} Banana, 1 Glass Milk"
        dinner_protein = "Chicken"
        evening = f"{banana//2} Banana, Milk"

    # ---------------- Final Diet ----------------
    diet = {
        "Breakfast": breakfast,
        "Lunch": f"{roti//2} Roti, {rice} Bowl Rice, Dal, Sabzi",
        "Evening Snack": evening,
        "Dinner": f"{roti//2} Roti, {dinner_protein}, Salad"
    }

    return jsonify({
        "bmi": round(bmi, 2),
        "target_bmi": round(target_bmi, 2),
        "category": category,
        "plan_type": plan_type,
        "calories": round(total_calories),
        "protein": round(protein),
        "carbs": round(carbs),
        "fats": round(fats),
        "diet": diet,
        "target_weight": target_weight,
        "note": "Eat clean, drink 3L water, train regularly 💪"
    })


if __name__ == "__main__":
    app.run(debug=True)