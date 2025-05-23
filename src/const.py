from enum import Enum, auto

class AgeGroup(Enum):
    """Age group IDs from KSÍ's system"""
    MEISTARAFLOKKUR = 1  # Senior team
    U23 = 31            # Under 23
    SECOND_FLOKKUR = 2  # U19
    THIRD_FLOKKUR = 3   # U16
    FOURTH_FLOKKUR = 4  # U14
    FIFTH_FLOKKUR = 420 # U12
    SIXTH_FLOKKUR = 6   # U10
    SEVENTH_FLOKKUR = 7 # U8
    
    @classmethod
    def get_name(cls, value):
        """Get human readable name for an age group ID"""
        for member in cls:
            if member.value == value:
                return member.name.replace('_', ' ').title()
        return f"Unknown Age Group ({value})"

class Team(Enum):
    """Team IDs from KSÍ's system"""
    # Reykjavík teams
    KR = 103
    FRAM = 104
    VALUR = 105
    VIKINGUR_R = 106
    THROTTUR_R = 107
    FJOLNIR = 112
    LEIKNIR_R = 111
    
    # Greater Reykjavík area
    BREIDABLIK = 200
    HK = 203
    GROTTA = 170
    AFTURELDING = 270
    STJARNAN = 210
    FH = 220
    HAUKAR = 221
    KEFLAVIK = 240
    
    # Other regions
    IA = 301  # Akranes
    KA = 601  # Akureyri
    THOR = 603  # Akureyri
    
    @classmethod
    def get_name(cls, value):
        """Get human readable name for a team ID"""
        for member in cls:
            if member.value == value:
                return member.name.replace('_', ' ').title()
        return f"Unknown Team ({value})" 