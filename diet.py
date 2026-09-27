"""
Nutrition calculation utilities for Nourish.

This module contains deterministic calculations only.
The language model is not involved in BMI, BMR, TDEE,
or calorie-target calculations.
"""

from typing import Final


# ============================================================
# CONSTANTS
# ============================================================

ACTIVITY_FACTORS: Final[dict[str, float]] = {
    "Sedentary": 1.20,
    "Lightly_Active": 1.375,
    "Moderately_Active": 1.55,
    "Very_Active": 1.725,
    "Extra_Active": 1.90,
}

CALORIE_ADJUSTMENTS: Final[dict[str, float]] = {
    "weight maintain": 0,
    "weight loss": -400,
    "weight gain": 300,
}

SUPPORTED_GENDERS: Final[set[str]] = {
    "male",
    "female",
}

SUPPORTED_GOALS: Final[set[str]] = set(
    CALORIE_ADJUSTMENTS.keys()
)


# ============================================================
# VALIDATION
# ============================================================

def _validate_positive(value: float, name: str) -> None:
    """Ensure a numeric input is greater than zero."""

    if value <= 0:
        raise ValueError(
            f"{name} must be greater than zero."
        )


def _validate_gender(gender: str) -> None:
    """Validate gender input used by the BMR equation."""

    if gender not in SUPPORTED_GENDERS:
        raise ValueError(
            f"Unsupported gender: {gender}. "
            f"Expected one of {sorted(SUPPORTED_GENDERS)}."
        )


def _validate_activity(activity: str) -> None:
    """Validate activity-level input."""

    if activity not in ACTIVITY_FACTORS:
        raise ValueError(
            f"Unsupported activity level: {activity}. "
            f"Expected one of {list(ACTIVITY_FACTORS.keys())}."
        )


def _validate_goal(aim: str) -> None:
    """Validate the user's selected goal."""

    if aim not in SUPPORTED_GOALS:
        raise ValueError(
            f"Unsupported goal: {aim}. "
            f"Expected one of {sorted(SUPPORTED_GOALS)}."
        )


# ============================================================
# BMI
# ============================================================

def bmi_calculator(weight: float, height: float) -> float:
    """
    Calculate Body Mass Index.

    Parameters
    ----------
    weight:
        Body weight in kilograms.

    height:
        Height in centimetres.

    Returns
    -------
    float
        BMI rounded to two decimal places.
    """

    _validate_positive(weight, "Weight")
    _validate_positive(height, "Height")

    height_meters = height / 100

    bmi = weight / (height_meters ** 2)

    return round(bmi, 2)


# ============================================================
# BMR
# ============================================================

def bmr_calculator(
    weight: float,
    height: float,
    age: int,
    gender: str,
) -> float:
    """
    Estimate Basal Metabolic Rate using the
    Mifflin-St Jeor equation.

    Weight is in kilograms.
    Height is in centimetres.
    """

    _validate_positive(weight, "Weight")
    _validate_positive(height, "Height")

    if age <= 0:
        raise ValueError("Age must be greater than zero.")

    _validate_gender(gender)

    base_bmr = (
        (10 * weight)
        + (6.25 * height)
        - (5 * age)
    )

    if gender == "male":
        bmr = base_bmr + 5
    else:
        bmr = base_bmr - 161

    return round(bmr, 2)


# ============================================================
# TDEE
# ============================================================

def tdee_calculator(
    bmr: float,
    activity: str,
) -> float:
    """
    Estimate Total Daily Energy Expenditure.

    TDEE = BMR × Activity Factor
    """

    _validate_positive(bmr, "BMR")
    _validate_activity(activity)

    activity_factor = ACTIVITY_FACTORS[activity]

    tdee = bmr * activity_factor

    return round(tdee, 2)


# ============================================================
# CALORIE TARGET
# ============================================================

def calorie_target(
    tdee: float,
    aim: str,
) -> float:
    """
    Estimate a daily calorie target based on TDEE and goal.

    Current project assumptions:
        Maintain → TDEE
        Weight loss → TDEE - 400 kcal
        Weight gain → TDEE + 300 kcal
    """

    _validate_positive(tdee, "TDEE")
    _validate_goal(aim)

    adjustment = CALORIE_ADJUSTMENTS[aim]

    target = tdee + adjustment

    # Prevent an invalid non-positive target.
    if target <= 0:
        raise ValueError(
            "Calculated calorie target must be greater than zero."
        )

    return round(target, 2)


# ============================================================
# OPTIONAL SUMMARY HELPER
# ============================================================

def calculate_nutrition_profile(
    weight: float,
    height: float,
    age: int,
    gender: str,
    activity: str,
    aim: str,
) -> dict[str, float]:
    """
    Calculate all core nutrition metrics together.

    This is useful for keeping the application layer clean.
    """

    bmi = bmi_calculator(weight, height)

    bmr = bmr_calculator(
        weight,
        height,
        age,
        gender,
    )

    tdee = tdee_calculator(
        bmr,
        activity,
    )

    calorie = calorie_target(
        tdee,
        aim,
    )

    return {
        "bmi": bmi,
        "bmr": bmr,
        "tdee": tdee,
        "calorie_target": calorie,
    }























# def bmi_calculator(weight, height): # Body Mass Index
#     bmi = weight / ((height/100)**2) # weight must be in kg and height in m (Conversion)
#     return round(bmi,2)

# def bmr_calculator(weight, height, age, gender): # Basal Metabolic Rate (Diff. for Male & Female)
#     if gender == "male":
#         bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
#         return bmr
#     elif gender == "female":
#         bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
#         return bmr

# def tdee_calculator(bmr, activity): # Total Daily Energy Expenditure (Activity Factor --> Some other factors)
#     #Define all the factors
#     activity_factor = {
#         "Sedentary": 1.20, 
#         "Lightly_Active": 1.375, 
#         "Moderately_Active": 1.55, 
#         "Very_Active": 1.725, 
#         "Extra_Active": 1.90
#     }
#     tdee = bmr * activity_factor[activity]
#     return round(tdee,2)

# def calorie_target(tdee, aim):
#     if aim == "weight maintain":
#         calorie = tdee
#     elif aim == "weight loss":
#         calorie = tdee - 400
#     elif aim == "weight gain": 
#         calorie = tdee + 300
#     return calorie

# # print(bmi_calculator(90, 180))
# # print(bmr_calculator(90, 170, 24, "male"))
# # bmr = bmr_calculator(90, 170, 24, "male")
# # print(tdee_calculator(bmr, "Moderately_Active"))
# # tdee = tdee_calculator(bmr, "Moderately_Active")
# # print("Your Final T")
# # print(calorie_target(tdee, "weight loss"))
