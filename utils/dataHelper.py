ingredients_input = "Identify only raw, uncooked food ingredients present in the image, such as fruits, vegetables, grains, spices, meat, or similar. Ignore any background elements (like trees, sky, birds) and cooked foods or meals. If no raw ingredients are detected, return an empty list. Respond only in the following JSON format without any explanation or extra text: { 'ingredients': ['ingredient1', 'ingredient2', 'ingredient3' ] } Only identify ingredients from the following list of 200 common raw food ingredients: chicken, egg, beef, pork, lamb, goat, duck, turkey, fish, shrimp, crab, lobster, mussel, clam, oyster, squid, octopus, milk, cheese, yogurt, butter, cream, apple, banana, orange, strawberry, blueberry, lemon, lime, mango, pineapple, watermelon, papaya, grape, cherry, peach, pear, plum, avocado, tomato, cucumber, lettuce, spinach, kale, arugula, cabbage, broccoli, cauliflower, zucchini, eggplant, bell pepper, chili pepper, beet, radish, squash, pumpkin, carrot, celery, onion, garlic, ginger, potato, sweet potato, yam, corn, peas, green beans, asparagus, mushroom, leek, chive, scallion, basil, cilantro, parsley, mint, dill, rosemary, thyme, oregano, sage, turmeric, cinnamon, clove, nutmeg, cardamom, cumin, coriander, mustard seed, sesame seed, sunflower seed, flaxseed, chia seed, almond, walnut, cashew, peanut, pistachio, hazelnut, macadamia, quinoa, rice, brown rice, oats, barley, millet, wheat, rye, buckwheat, chickpea, lentil, black bean, kidney bean, navy bean, pinto bean, lima bean, mung bean, soybeans, tofu, coconut, date, fig, raisin, apricot, olive, spinach, swiss chard, collard greens, mustard greens, watercress, seaweed, nori, wakame, kombu, bamboo shoot, jicama, lotus root, daikon, kohlrabi, cassava, taro, yam bean, plantain, jackfruit, durian, dragonfruit, guava, lychee, starfruit, rambutan, tamarind, horseradish, wasabi, vinegar, vanilla bean, cocoa beans, cacao nibs, acai berry, goji berry, mulberry, sorrel, amaranth, farro, spelt, bulgur, wild rice, white rice, teff, salsify, sprouts, bean sprout, alfalfa sprout, clover sprout, broccoli sprout"


def getRecipesInput(ingredients_str):
    return f"""
        Based on the following ingredients: {ingredients_str}.

        Generate exactly 5 creative and delicious recipes. Please provide the response as a single JSON object with a key "recipes" which contains a list of 5 recipe objects.

        Each recipe object must have the following structure and data types:
        - "id": a unique string.
        - "title": a string.
        - "description": a brief, enticing string description of the dish.
        - "rating": a float between 4.0 and 5.0.
        - "reviewCount": an integer.
        - "cookTime": a string (e.g., "30 mins").
        - "prepTime": a string (e.g., "15 mins").
        - "servings": a string (e.g., "4").
        - "difficulty": a string ("Easy", "Medium", or "Hard").
        - "ingredients": a list of objects, where each object has "quantity" (float or integer), "unit" (string), and "name" (string).
        - "instructions": a list of strings, where each string is a complete step in the cooking process from start to finish.

        Do not include any explanation, introductory text, or markdown formatting like ```json. And never include cookTime and prepTime equal to 0. Your response must be only the raw JSON object.
        """
    
# end def