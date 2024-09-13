import random
from app import db

names = [
    'Dominique Chandler', 'Yong Baxter',
    'Rich Dean', 'Kristine Dickerson', 'Mickey Romero', 'Keri Pennington', 'Julio Ali', 'Broderick Atkins', 'Carlos Kaufman', 'Dominick Ramos', 'Colton Pitts',
    'Marlin Wu', 'Ed Dillon', 'Dorsey Rivera', 'Adalberto Nixon', 'Pearlie Shepard', 'Saul Burton', 'Melvin Flores', 'Nestor Ray', 'Brent Welch', 'Deon Foley',
    'Jc Crawford', 'Rubin Armstrong', 'Cordell Parsons', 'Susanna Pearson', 'Brian Clark', 'Deena Melendez', 'Kathrine Hayden', 'Coy Khan', 'Alyssa Wang',
    'Stacy Montoya', 'Dennis Downs', 'Jacklyn Jefferson', 'Nicky Ramsey', 'Jeromy Moreno', 'Jackson Horn', 'Sheri Bailey',
    'Luis George', 'Lewis Zuniga', 'Alexandra Dickson', 'Stacey Johnston', 'Margret Mckenzie', 'Lon Mcclure', 'Ken Ashley', 'Joanna Brandt',
    'Carla Combs','Krista Mcguire','Brittney Cortez','Michelle Cannon','Francine Noble',
]

adjectives = [
    'cloistered', 'shaggy', 'hallowed', 'truthful', 'one', 'painful', 'thin',
    'talented', 'various', 'loving', 'fretful', 'capricious', 'placid', 'steady',
    'sincere', 'symptomatic', 'probable', 'rotten', 'juvenile', 'depressed', 'yielding',
    'sick', 'gorgeous', 'wide-eyed', 'materialistic', 'visible', 'delightful', 'debonair',
    'married', 'neat', 'uttermost', 'needy', 'disagreeable', 'breakable', 'crooked', 'sedate', 
    'silly', 'wet', 'bizarre', 'creepy', 'pleasant', 'flagrant', 'clever', 'utopian', 'slimy', 
    'organic', 'discreet', 'picayune', 'dramatic', 'hurt'
    ]
nouns = [
    'policy', 'gate', 'examination', 'engineering', 'cell', 'garbage', 'variation', 'statement', 
    'permission', 'collection', 'preparation', 'insurance', 'message', 'climate', 'manager', 'music', 
    'preference', 'family', 'football', 'product', 'context', 'entry', 'wife', 'injury', 'difference', 
    'uncle', 'gene', 'measurement', 'success', 'resolution', 'bonus', 'student', 'fortune', 'celebration', 
    'movie', 'king', 'honey', 'law', 'sir', 'elevator', 'thing', 'article', 'method', 'language', 'classroom', 
    'opportunity', 'funeral', 'clothes', 'situation', 'cancer'
    ]

connectors = ['of', 'in', 'under', 'beyond', 'through', 'beneath', 'above', 'without']

def generate_title():
    structure = random.choice([
        "{} {}",
        "The {} {}",
        "{} {} of {}",
        "The {} {} of the {}",
        "{} of the {}",
        "{} in the {}",
    ])
    
    words = random.sample(adjectives + nouns + connectors, 3)
    return structure.format(*words).title()

def generate_name():
    return random.choice(names)

