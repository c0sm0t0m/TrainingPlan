"""
Trainer Style Configurations for AI Training Plan Generation

Based on research of world-renowned endurance coaches and their methodologies.
Each trainer has a unique approach to periodization, intensity distribution, and training philosophy.

These configurations can be selected by users to customize their training plan generation.
Users can also create custom trainer profiles based on these templates.
"""

from typing import Dict, Any, List


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TRAINER PROFILES - TOP 10 ENDURANCE COACHES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TRAINER_STYLES: Dict[str, Dict[str, Any]] = {
    
    # 1. JOE FRIEL - Periodization Pioneer
    "joe_friel": {
        "name": "Joe Friel",
        "tagline": "The Periodization Pioneer",
        "description": "Creator of 'The Triathlete's Training Bible'. Emphasizes structured periodization with clear training phases, progressive overload, and data-driven training using TSS/CTL metrics.",
        "philosophy": """Joe Friel's Training Philosophy:
        
• PERIODIZATION: Clear base, build, peak, and taper phases
• TRAINING STRESS SCORE: Use TSS to quantify training load
• PROGRESSIVE OVERLOAD: Gradual increase in volume and intensity
• RECOVERY: Strategic rest weeks every 3-4 weeks (20-30% volume reduction)
• LIMITER-BASED: Focus training on individual weaknesses
• RACE-SPECIFIC: Peak workouts mimic race demands
• 3-WEEK BUILD + 1-WEEK RECOVERY: Proven cycle structure
• BRICK SESSIONS: Bike-to-run transitions for triathletes
• ANNUAL TRAINING PLAN: Long-term macro cycle planning""",
        
        "training_distribution": {
            "base_phase": "70% Zone 1-2 (aerobic base), 20% Zone 3 (tempo), 10% Zone 4-5",
            "build_phase": "60% Zone 1-2, 20% Zone 3, 20% Zone 4-5 (increasing intensity)",
            "peak_phase": "50% Zone 1-2, 20% Zone 3, 30% Zone 4-5 (race-specific)",
            "taper_phase": "80% Zone 1-2, 10% Zone 3, 10% Zone 4-5 (maintain intensity, reduce volume)"
        },
        
        "key_workouts": [
            "Tempo intervals (Zone 3) - 3x10-20min",
            "Threshold intervals (Zone 4) - 4-6x5min",
            "VO2max intervals (Zone 5) - 5-8x3min",
            "Long endurance rides/runs - 2-4 hours Zone 2",
            "Brick workouts - Bike 60min + Run 20min",
            "Race-simulation workouts in peak phase"
        ],
        
        "periodization_structure": {
            "base_weeks": "4-8 weeks: Build aerobic base, perfect technique",
            "build_weeks": "6-8 weeks: Increase intensity, maintain volume",
            "peak_weeks": "3-4 weeks: Race-specific intensity, reduced volume",
            "taper_weeks": "2-3 weeks: Maintain intensity, drastically reduce volume (50-70%)"
        },
        
        "recovery_strategy": "Every 3rd or 4th week is a recovery week with 20-30% reduced volume. Emphasis on listening to body, adequate sleep, and nutrition.",
        
        "special_emphasis": [
            "Weekly TSS targets based on CTL progression",
            "Structured intervals with precise power/pace zones",
            "Comprehensive testing every 4-6 weeks",
            "Detailed workout notes and execution feedback",
            "Taper starts 2-3 weeks before A-race"
        ]
    },
    
    # 2. MAT FITZGERALD - 80/20 Endurance
    "mat_fitzgerald": {
        "name": "Matt Fitzgerald",
        "tagline": "The 80/20 Endurance Advocate",
        "description": "Author of '80/20 Running' and '80/20 Triathlon'. Advocates for polarized training: 80% low intensity, 20% high intensity, based on research showing elite athletes train mostly easy.",
        "philosophy": """Matt Fitzgerald's 80/20 Training Philosophy:
        
• 80/20 RULE: 80% of training at low intensity (Zone 1-2), 20% at moderate-high (Zone 3-5)
• POLARIZED TRAINING: Avoid 'gray zone' (Zone 3) - go easy or go hard
• VOLUME FIRST: Build aerobic base with high volume of easy running
• LESS IS MORE: Quality over quantity for hard workouts
• ENJOYMENT: Training should be sustainable and enjoyable
• LONG RUNS: Critical for endurance development
• ADAPTIVE RUNNING: Run by feel, not strictly by zones
• RACE-PACE WORKOUTS: Practice goal race pace regularly
• CROSS-TRAINING: Include cycling/swimming to reduce injury risk""",
        
        "training_distribution": {
            "year_round": "80% Zone 1-2 (easy), 15% Zone 4-5 (hard), 5% Zone 3 (tempo)",
            "base_phase": "85% Zone 1-2, 10% Zone 4, 5% Zone 5",
            "build_phase": "75% Zone 1-2, 15% Zone 4-5, 10% Zone 3",
            "race_phase": "80% Zone 1-2, 20% Zone 4-5 (race pace)"
        },
        
        "key_workouts": [
            "Easy runs - majority of training, conversational pace",
            "Long runs - 90-120min+ at easy pace (Zone 2)",
            "Fast finish long runs - last 15-20min at tempo",
            "VO2max intervals - 5-8x800m or 4-6x1000m",
            "Threshold intervals - 3-4x1 mile at threshold pace",
            "Race-pace workouts - sustained efforts at goal pace"
        ],
        
        "periodization_structure": {
            "base_weeks": "6-8 weeks: High volume, 85% easy",
            "build_weeks": "6-8 weeks: Maintain volume, add intensity (still 80/20)",
            "peak_weeks": "4-6 weeks: Race-specific, 80% easy, 20% hard",
            "taper_weeks": "2 weeks: Reduce volume 50%, maintain intensity"
        },
        
        "recovery_strategy": "Recovery through easy training volume. Avoid 'junk miles' in Zone 3. Use easy days for true recovery while maintaining consistency.",
        
        "special_emphasis": [
            "STRICT adherence to 80/20 intensity distribution",
            "No moderate-intensity 'gray zone' training",
            "Run by FEEL on easy days (ignore pace/HR if feeling good)",
            "Hard days are HARD - don't hold back on intervals",
            "Long runs build mental toughness and fat adaptation",
            "Minimal taper - fitness doesn't disappear in 2 weeks"
        ]
    },
    
    # 3. JACK DANIELS - VDOT Training
    "jack_daniels": {
        "name": "Jack Daniels",
        "tagline": "The VDOT Training Legend",
        "description": "Legendary running coach and author of 'Daniels' Running Formula'. Created the VDOT system for calculating training paces. Emphasizes scientific approach with specific pace zones.",
        "philosophy": """Jack Daniels' VDOT Training Philosophy:
        
• VDOT SYSTEM: Science-based training paces calculated from current fitness
• SPECIFIC TRAINING PACES: Each workout has a precise purpose and pace
• QUALITY OVER QUANTITY: Every run has specific physiological benefit
• E (Easy), M (Marathon), T (Threshold), I (Interval), R (Repetition) paces
• PROGRESSIVE TRAINING: Gradual adaptation through systematic stress
• OPTIMAL TRAINING STRESS: Not too little, not too much
• PHASE-SPECIFIC WORKOUTS: Different phases emphasize different energy systems
• TESTING: Regular time trials to update VDOT and training paces
• 4-WEEK CYCLES: Consistent training blocks with built-in recovery""",
        
        "training_distribution": {
            "base_phase": "75% Easy pace, 15% Threshold, 10% Intervals",
            "build_phase": "60% Easy, 20% Threshold, 15% Intervals, 5% Repetitions",
            "peak_phase": "55% Easy, 15% Marathon pace, 20% Threshold, 10% Intervals",
            "taper_phase": "70% Easy, 20% Marathon/Threshold, 10% Intervals (short, sharp)"
        },
        
        "key_workouts": [
            "E (Easy) runs - 65-79% max HR, conversational",
            "T (Threshold) runs - 15-20min continuous or intervals (5x1000m)",
            "I (Interval) runs - 3-5min at VO2max (5-6x1000m)",
            "R (Repetition) runs - 200-400m at 5K pace or faster",
            "M (Marathon) pace runs - sustained efforts at goal race pace",
            "Long runs - 25-30% of weekly mileage at E pace"
        ],
        
        "periodization_structure": {
            "phase_1_base": "4 weeks: Build mileage with E and T work",
            "phase_2_intervals": "4 weeks: Add I workouts, maintain T work",
            "phase_3_race_prep": "4 weeks: Add M pace, maintain I/T work",
            "phase_4_peak": "2-3 weeks: Race-specific, reduce volume"
        },
        
        "recovery_strategy": "Built-in recovery through E pace runs. Hard days followed by easy days. Recovery weeks not always necessary if training is properly structured.",
        
        "special_emphasis": [
            "Calculate VDOT from recent race or time trial",
            "NEVER exceed prescribed training paces",
            "Each pace has specific physiological purpose",
            "Quality (intensity) > Quantity (volume)",
            "Long runs should NOT be race pace - stay easy",
            "Threshold runs improve lactate clearance",
            "Interval training improves VO2max",
            "Test every 6-8 weeks to update VDOT"
        ]
    },
    
    # 4. STEPHEN SEILER - Polarized Training Pioneer
    "stephen_seiler": {
        "name": "Stephen Seiler",
        "tagline": "The Polarized Training Scientist",
        "description": "Exercise scientist who researched elite athletes and discovered they train with a polarized distribution. Advocates for high volume at low intensity with strategic high-intensity sessions.",
        "philosophy": """Stephen Seiler's Polarized Training Philosophy:
        
• POLARIZED DISTRIBUTION: ~80% Zone 1-2, ~20% Zone 4-5, minimal Zone 3
• THRESHOLD IS DANGEROUS: Zone 3 accumulates fatigue without adaptations
• VOLUME AT LOW INTENSITY: Build massive aerobic base
• INTENSITY IN HIGH ZONE: When going hard, go HARD (VO2max)
• CONSISTENCY: Sustainable training year-round without burnout
• RECOVERY-FOCUSED: Easy training promotes recovery while maintaining fitness
• 2-3 HARD SESSIONS PER WEEK: More intensity doesn't improve results
• INTERVAL VARIETY: 4x8min, 5x4min, 30-30 intervals
• PATIENCE: Aerobic development takes months/years""",
        
        "training_distribution": {
            "all_phases": "75-80% Zone 1 (very easy), 5% Zone 2 (easy), <5% Zone 3, 10-15% Zone 4-5 (hard)",
            "base_phase": "85% Zone 1-2, 15% Zone 4-5 (no Zone 3)",
            "competitive_phase": "75% Zone 1-2, 25% Zone 4-5 (more high-intensity)",
            "taper_phase": "80% Zone 1-2, 20% Zone 4-5 (short, sharp sessions)"
        },
        
        "key_workouts": [
            "Long slow distance - 2-4 hours Zone 1 (truly easy)",
            "4x8min intervals at Zone 4 (threshold/VO2max border)",
            "5x4min intervals at Zone 5 (VO2max)",
            "6x4min at 90-95% max HR with 2min recovery",
            "Pyramid intervals - 4-5-6-5-4min",
            "30-30 intervals - 30sec hard, 30sec easy for 20-40min"
        ],
        
        "periodization_structure": {
            "base_phase": "8-12 weeks: High volume Zone 1, minimal intensity",
            "pre_competitive": "6-8 weeks: Add 2 hard sessions/week",
            "competitive": "4-8 weeks: Maintain polarized, race regularly",
            "recovery": "2-4 weeks: Reduce volume, maintain some intensity"
        },
        
        "recovery_strategy": "Recovery IS training. Zone 1 sessions promote active recovery while building aerobic capacity. Hard sessions spaced 2-3 days apart.",
        
        "special_emphasis": [
            "AVOID 'tempo' or Zone 3 training - it's metabolic purgatory",
            "Easy days MUST be easy (can hold conversation)",
            "Hard days MUST be hard (uncomfortable, challenging)",
            "2-3 high-intensity sessions per week is optimal",
            "More intensity does NOT equal better results",
            "Volume + polarization = sustainable performance",
            "HRV monitoring to manage intensity sessions",
            "Long-term consistency beats short-term intensity"
        ]
    },
    
    # 5. RENATO CANOVA - Marathon Master
    "renato_canova": {
        "name": "Renato Canova",
        "tagline": "The Marathon Master",
        "description": "Italian coach of world-class marathoners. Known for innovative marathon-specific training including long runs with speed changes, altitude training, and aggressive race-pace work.",
        "philosophy": """Renato Canova's Marathon Training Philosophy:
        
• MARATHON-SPECIFIC TRAINING: Every workout has purpose for 42K
• VARIED LONG RUNS: Mix easy pace with marathon pace, half-marathon pace, threshold
• HIGH QUALITY: Hard sessions are very specific and intense
• ALTITUDE TRAINING: Use altitude camps for aerobic development
• RACE AS TRAINING: Use half marathons and shorter races as training
• FUNDAMENTAL ENDURANCE: Long aerobic runs at steady pace (no slow jogging)
• MARATHON RHYTHM: Practice goal marathon pace in various contexts
• MENTAL TOUGHNESS: Train the mind to push through discomfort
• PROGRESSIVE LONG RUNS: Start easy, finish at marathon pace or faster""",
        
        "training_distribution": {
            "base_phase": "70% Fundamental endurance (steady), 20% Long runs, 10% Easy recovery",
            "build_phase": "50% Fundamental, 25% Marathon-specific, 15% Threshold, 10% Easy",
            "specific_phase": "40% Fundamental, 35% Marathon pace, 15% Fast long runs, 10% Easy",
            "taper_phase": "50% Easy, 30% Marathon pace (short), 20% Fundamental"
        },
        
        "key_workouts": [
            "Long run with progression - 30K total, last 10K at marathon pace",
            "Marathon-pace long run - 25-35K at goal race pace",
            "Mixed long run - 8K easy + 10K marathon pace + 8K easy",
            "Fartlek long run - 20-30K with random speed surges",
            "Long threshold run - 15-20K at half-marathon pace",
            "Double threshold - AM: 10K tempo, PM: 10K tempo"
        ],
        
        "periodization_structure": {
            "fundamental_phase": "4-6 weeks: Aerobic base, fundamental endurance",
            "specific_marathon": "8-10 weeks: Marathon-pace work, long runs with quality",
            "race_specific": "4-6 weeks: Aggressive marathon-pace sessions",
            "final_taper": "10-14 days: Sharp reduction, maintain sharpness"
        },
        
        "recovery_strategy": "Easy runs are for recovery only. Hard sessions require full recovery (48-72 hours). Listen to body, adjust based on fatigue levels.",
        
        "special_emphasis": [
            "Long runs are NOT slow runs - maintain 'fundamental' pace",
            "Practice marathon pace in FATIGUED state (end of long runs)",
            "Use half marathons as hard training sessions",
            "Double days (AM/PM) to increase volume without injury",
            "Altitude camps boost aerobic capacity significantly",
            "Mental rehearsal during long runs with speed changes",
            "Progressive long runs simulate marathon fatigue",
            "Final taper is short (10-14 days max)"
        ]
    },
    
    # 6. PHIL MAFFETONE - Low Heart Rate Training
    "phil_maffetone": {
        "name": "Phil Maffetone",
        "tagline": "The Low Heart Rate Training Pioneer",
        "description": "Developer of MAF (Maximum Aerobic Function) training method. Emphasizes aerobic base building through low heart rate training (180-age formula) before adding intensity.",
        "philosophy": """Phil Maffetone's MAF Training Philosophy:
        
• MAF FORMULA: Train at 180 minus age (or 180-age-10 if detrained)
• AEROBIC BASE FIRST: 2-6 months of ONLY aerobic training before intensity
• NO ANAEROBIC TRAINING: Until aerobic system is fully developed
• FAT ADAPTATION: Train body to burn fat efficiently
• LONG-TERM DEVELOPMENT: Patience - results take months
• HOLISTIC HEALTH: Nutrition, stress, sleep affect training
• MAF TEST: Monthly time trials at MAF HR to track progress
• CONSISTENCY: Daily aerobic training builds foundation
• INJURY PREVENTION: Low-intensity reduces injury risk""",
        
        "training_distribution": {
            "base_phase": "100% at MAF heart rate or below (no exceptions)",
            "developed_base": "90% MAF pace, 10% tempo (only after 3-6 months base)",
            "racing_phase": "80% MAF, 10% tempo, 10% race pace/intervals",
            "maintenance": "85% MAF, 15% intensity (maintain aerobic base)"
        },
        
        "key_workouts": [
            "MAF runs - run at 180-age heart rate",
            "Long aerobic run - 90-120min at MAF HR",
            "MAF test - time trial at MAF HR on same route monthly",
            "Easy recovery - below MAF HR (conversational)",
            "Once base is built: tempo runs (limited)",
            "Once base is built: race-pace work (1x/week max)"
        ],
        
        "periodization_structure": {
            "aerobic_base_building": "3-6 months: 100% at MAF HR or below",
            "anaerobic_development": "2-3 months: Add 1-2 intensity sessions/week",
            "racing_season": "2-3 months: Maintain aerobic, race regularly",
            "recovery_phase": "4-8 weeks: Return to pure MAF training"
        },
        
        "recovery_strategy": "Aerobic training IS recovery. All training below MAF HR promotes recovery while building fitness. Listen to body, adjust training if fatigued.",
        
        "special_emphasis": [
            "Calculate MAF HR: 180 - age (adjust -5 to -10 if injured/detrained)",
            "STRICT adherence to MAF HR - no cheating",
            "Expect initial slowness - it's temporary",
            "MAF pace will improve 30-60sec/km over months",
            "Do monthly MAF test to track aerobic development",
            "Fix diet: reduce sugar, increase healthy fats",
            "Manage stress - cortisol sabotages aerobic development",
            "NO intensity until aerobic base is built (3-6 months)",
            "Be patient - this is long-term development"
        ]
    },
    
    # 7. BRAD HUDSON - Adaptive Running
    "brad_hudson": {
        "name": "Brad Hudson",
        "tagline": "The Adaptive Running Coach",
        "description": "Author of 'Run Faster'. Emphasizes adaptive training based on daily form, progressive runs, and medium-long runs. Flexible approach focused on effort over strict pace.",
        "philosophy": """Brad Hudson's Adaptive Running Philosophy:
        
• ADAPTIVE TRAINING: Adjust daily training based on how you feel
• RUN BY EFFORT: Trust perceived effort over pace/HR
• MEDIUM-LONG RUNS: 75-90min runs are most effective
• PROGRESSIVE RUNS: Start easy, finish strong
• HILL TRAINING: Essential for strength and power
• FUNDAMENTAL WORKOUTS: Build around key sessions
• VARIETY: Mix paces, terrains, distances
• INTUITIVE TRAINING: Develop 'feel' for effort levels
• STRENGTH ENDURANCE: Long tempo efforts build marathon fitness""",
        
        "training_distribution": {
            "typical_week": "60% Easy, 20% Steady state, 10% Threshold, 10% VO2max",
            "base_phase": "70% Easy, 20% Steady state, 10% Hills/tempo",
            "build_phase": "55% Easy, 25% Steady/threshold, 15% VO2max, 5% Speed",
            "race_phase": "60% Easy, 20% Race pace, 15% Threshold, 5% VO2max"
        },
        
        "key_workouts": [
            "Medium-long run - 75-90min steady state",
            "Progressive long run - start easy, finish 10K at tempo",
            "Hill repetitions - 8-12x90sec hills",
            "Tempo run - 20-40min at threshold effort",
            "VO2max intervals - 5-6x1K or 3-4x1 mile",
            "Long run with surge - insert 3-5min surges at threshold"
        ],
        
        "periodization_structure": {
            "base_phase": "4-6 weeks: Build mileage, medium-long runs, hills",
            "strength_phase": "4-6 weeks: Add tempo work, maintain hills",
            "speed_phase": "4-6 weeks: Add VO2max work, reduce volume slightly",
            "race_phase": "2-4 weeks: Sharpen with race-pace work, reduce volume"
        },
        
        "recovery_strategy": "Recovery runs are short and easy. Listen to body daily - skip or modify workouts if fatigued. Better to undertrain than overtrain.",
        
        "special_emphasis": [
            "ADAPT workouts daily based on how you feel",
            "Medium-long runs (75-90min) are secret weapon",
            "Progressive runs teach pacing and mental toughness",
            "Hill training builds strength without injury risk",
            "Run by EFFORT, not pace - forget the watch sometimes",
            "Mix terrains: roads, trails, tracks",
            "Develop intuition for effort levels",
            "Recovery runs should feel EASY, regardless of pace",
            "Key workouts: don't miss them or compromise quality"
        ]
    },
    
    # 8. GREG MCMILLAN - Goal-Based Training
    "greg_mcmillan": {
        "name": "Greg McMillan",
        "tagline": "The Goal-Based Training Expert",
        "description": "Creator of McMillan Running Calculator. Emphasizes goal-specific training with precise training paces calculated from current fitness and race goals.",
        "philosophy": """Greg McMillan's Goal-Based Training Philosophy:
        
• GOAL-SPECIFIC TRAINING: Every workout targets your race goal
• TRAINING PACE CALCULATOR: Use current fitness to calculate optimal training paces
• BALANCED TRAINING: Equal emphasis on endurance, stamina, speed
• SIMULATION WORKOUTS: Practice race conditions and pacing
• RECOVERY RUNS: Essential for adaptation and injury prevention
• WORKOUT PROGRESSION: Gradually increase difficulty of key workouts
• TESTING: Regular time trials to update training paces
• TAPER PROPERLY: 2-3 weeks with reduced volume, maintained intensity
• MENTAL PREPARATION: Visualize race scenarios during training""",
        
        "training_distribution": {
            "base_phase": "65% Recovery pace, 25% Endurance pace, 10% Easy tempo",
            "stamina_phase": "55% Recovery, 20% Endurance, 15% Tempo, 10% Threshold",
            "speed_phase": "50% Recovery, 20% Endurance, 15% Interval, 10% Repetition, 5% Speed",
            "race_phase": "60% Recovery, 15% Endurance, 15% Race pace, 10% Speed"
        },
        
        "key_workouts": [
            "Recovery run - very easy, conversational",
            "Long run - endurance pace for 90-120min",
            "Tempo run - 20-40min at comfortably hard pace",
            "Threshold intervals - 3-5x1 mile at threshold",
            "VO2max intervals - 5-6x1000m at interval pace",
            "Race-pace long run - practice goal race pace"
        ],
        
        "periodization_structure": {
            "endurance_phase": "4-6 weeks: Build aerobic base, long runs",
            "stamina_phase": "4-6 weeks: Add tempo and threshold work",
            "speed_phase": "4-6 weeks: Add VO2max and race-pace work",
            "taper_phase": "2-3 weeks: Reduce volume 50-70%, keep intensity"
        },
        
        "recovery_strategy": "Recovery runs at truly easy pace (2-3min/km slower than race pace). Every hard workout followed by 1-2 easy days. Sleep and nutrition are priorities.",
        
        "special_emphasis": [
            "Use McMillan calculator to find training paces",
            "Update training paces after breakthrough workouts",
            "Practice goal race pace in various contexts",
            "Simulation workouts mimic race conditions",
            "Balance endurance, stamina, and speed training",
            "Recovery runs prevent overtraining",
            "Don't skip recovery - it's when adaptation happens",
            "Mental rehearsal during training builds confidence",
            "Taper is critical - don't undertaper"
        ]
    },
    
    # 9. DAVE SCOTT - Triathlon Legend
    "dave_scott": {
        "name": "Dave Scott",
        "tagline": "The Triathlon Legend",
        "description": "6-time Ironman World Champion. Emphasizes high-volume training with attention to all three sports. Known for intense training camps and mental toughness development.",
        "philosophy": """Dave Scott's Triathlon Training Philosophy:
        
• SWIM, BIKE, RUN: Equal development of all three sports
• HIGH VOLUME: Build capacity through consistent volume
• BRICK SESSIONS: Essential for triathlon-specific fitness
• TECHNIQUE FIRST: Perfect form in all three disciplines
• MENTAL TOUGHNESS: Training prepares mind as much as body
• NUTRITION: Proper fueling and hydration is critical
• TRANSITIONS: Practice T1 and T2 efficiency
• OPEN WATER SKILLS: Pool swimming is not enough
• STRENGTH TRAINING: Support endurance with functional strength""",
        
        "training_distribution": {
            "base_phase": "Swim 20%, Bike 40%, Run 30%, Strength 10% - all easy/moderate",
            "build_phase": "Swim 20%, Bike 35%, Run 35%, Strength 10% - add intensity",
            "peak_phase": "Swim 15%, Bike 40%, Run 35%, Brick 10% - race-specific",
            "taper_phase": "Swim 20%, Bike 35%, Run 35%, Brick 10% - reduce volume 50%"
        },
        
        "key_workouts": [
            "Long bike - 3-5 hours at steady endurance pace",
            "Bike intervals - 5x5min at threshold power",
            "Long run - 90-150min at easy to moderate pace",
            "Brick workout - 90min bike + 45min run",
            "Swim intervals - 10x100m at threshold pace",
            "Open water swim - 60-90min continuous",
            "Hill repeats (run or bike) - build strength"
        ],
        
        "periodization_structure": {
            "base_building": "8-12 weeks: Build volume in all three sports",
            "intensity_build": "6-8 weeks: Add threshold/tempo work",
            "race_specific": "4-6 weeks: Brick sessions, race pace",
            "taper": "2-3 weeks: Reduce volume, maintain intensity"
        },
        
        "recovery_strategy": "Active recovery through easy swimming. Rest days are rare - recovery is active. Massage, stretching, and proper nutrition support recovery.",
        
        "special_emphasis": [
            "BRICK SESSIONS are non-negotiable for triathletes",
            "Practice nutrition and hydration in training",
            "Open water swimming builds confidence",
            "Perfect transitions - time saved is time earned",
            "Mental visualization during long sessions",
            "Strength training prevents injury",
            "High volume requires meticulous recovery",
            "Simulate race conditions (early morning, nutrition, etc.)",
            "Build toughness through training camps"
        ]
    },
    
    # 10. PETE MAGILL - Masters Running Specialist
    "pete_magill": {
        "name": "Pete Magill",
        "tagline": "The Masters Running Specialist",
        "description": "American record holder for masters runners. Author focusing on training for runners over 40. Emphasizes recovery, injury prevention, and maintaining speed as we age.",
        "philosophy": """Pete Magill's Masters Running Philosophy:
        
• RECOVERY FIRST: Masters athletes need more recovery
• MAINTAIN SPEED: Use it or lose it - keep fast-twitch fibers active
• STRENGTH TRAINING: Essential for injury prevention and power
• EASY RUNS EASIER: Truly easy pace allows better recovery
• HARD RUNS HARDER: Short, intense sessions maintain speed
• INJURY PREVENTION: Listen to body, back off when needed
• BIOMECHANICS: Maintain good form, avoid age-related deterioration
• CONSISTENCY: Regular training beats sporadic intensity
• SMART PROGRESSION: Gradual increases prevent injury""",
        
        "training_distribution": {
            "weekly": "60% Easy, 20% Steady/tempo, 10% Threshold, 10% Speed/intervals",
            "base_phase": "70% Easy, 20% Steady, 5% Tempo, 5% Speed",
            "build_phase": "55% Easy, 20% Steady, 15% Threshold, 10% VO2max",
            "race_phase": "60% Easy, 15% Steady, 15% Race pace, 10% Speed"
        },
        
        "key_workouts": [
            "Easy runs - VERY easy, recovery-focused",
            "Long run - 90-120min at conversational pace",
            "Tempo run - 20min at comfortably hard pace",
            "Short intervals - 8-10x400m at 5K pace (maintain speed)",
            "Hill sprints - 6-8x10-12sec explosive efforts",
            "Strides - 6-8x100m at mile pace (neuromuscular)"
        ],
        
        "periodization_structure": {
            "base_phase": "6-8 weeks: Build mileage carefully, lots of easy running",
            "strength_phase": "4-6 weeks: Add tempo work and strength training",
            "speed_phase": "4-6 weeks: Add intervals, maintain strength",
            "race_phase": "4-6 weeks: Race-specific work, reduced volume"
        },
        
        "recovery_strategy": "Extra recovery days (2-3/week completely off). Massage, foam rolling, mobility work. Sleep 8+ hours. Nutrition focused on anti-inflammatory foods.",
        
        "special_emphasis": [
            "Masters runners NEED more recovery - take it",
            "Do STRIDES 2-3x/week - maintain speed/form",
            "Strength training 2x/week (prevents injury)",
            "Easy runs should feel EASY - no ego",
            "Short, intense intervals maintain fast-twitch fibers",
            "Listen to body - chronic pain is a warning",
            "Warm up longer (10-15min minimum)",
            "Cool down and stretch after hard workouts",
            "Recovery weeks every 3 weeks (not 4)",
            "Consistency beats intensity for masters"
        ]
    },
    
    # 11. DAN LORANG - Precision Triathlon Coaching
    "dan_lorang": {
        "name": "Dan Lorang",
        "tagline": "The Precision Triathlon Coach",
        "description": "Coach of Jan Frodeno (3x Ironman World Champion, Olympic Gold). Emphasizes scientific precision, data-driven training, high-volume bike focus, and race-specific preparation with German efficiency.",
        "philosophy": """Dan Lorang's Precision Training Philosophy:
        
• DATA-DRIVEN PRECISION: Every workout has measurable targets and outcomes
• HIGH-VOLUME CYCLING: Cycling is the differentiator in long-course triathlon
• RACE-SPECIFIC BLOCKS: Intensive 2-4 week camps mimicking race conditions
• HEAT ADAPTATION: Deliberate heat exposure for Kona preparation
• MARGINAL GAINS: Optimize everything - nutrition, equipment, pacing
• THRESHOLD DEVELOPMENT: Sustained power/pace at threshold is critical
• MENTAL PREPARATION: Visualization and race scenario rehearsal
• RECOVERY PROTOCOLS: Structured recovery (massage, compression, nutrition)
• GERMAN EFFICIENCY: Systematic, methodical, no wasted training""",
        
        "training_distribution": {
            "base_phase": "Swim 15%, Bike 50%, Run 25%, Strength 10% - build aerobic engine",
            "build_phase": "Swim 15%, Bike 45%, Run 30%, Brick 10% - increase intensity",
            "race_specific": "Swim 12%, Bike 48%, Run 30%, Race simulation 10%",
            "peak_phase": "Swim 10%, Bike 50%, Run 25%, Race pace 15% - sharpen"
        },
        
        "key_workouts": [
            "Long bike - 5-7 hours at IM pace, practice nutrition",
            "Bike threshold intervals - 3-5x20min at FTP",
            "Bike-run brick - 4 hours bike + 90min run at race pace",
            "Run threshold - 60-75min at IM pace or faster",
            "Swim CSS intervals - 10-15x100m at critical swim speed",
            "Race simulation - 5-6 hour bike + 2-3 hour run",
            "Heat training - indoor sessions in hot conditions"
        ],
        
        "periodization_structure": {
            "base_phase": "8-12 weeks: High volume, build aerobic capacity",
            "build_phase": "8-10 weeks: Add threshold work, maintain volume",
            "race_specific_camps": "2-3 intensive 2-4 week blocks with race simulation",
            "taper_phase": "14-18 days: Reduced volume, maintain intensity sharpness"
        },
        
        "recovery_strategy": "Structured recovery protocols: compression gear, massage, ice baths, nutrition timing. Recovery weeks integrated into camps (3 weeks hard, 1 week easier).",
        
        "special_emphasis": [
            "Bike volume is CRITICAL - Ironman is won on the bike",
            "Practice race nutrition EXACTLY in training",
            "Heat adaptation if racing in hot conditions",
            "Power-based training for cycling (use power meter)",
            "Pace-based running (not HR) for race specificity",
            "Swim technique over volume (efficiency first)",
            "Brick workouts weekly in race-specific phase",
            "Mental rehearsal of race scenarios",
            "Short taper (14-18 days max) - maintain fitness"
        ]
    },
    
    # 12. NATASHA VAN DER MERWE - Holistic Performance
    "natasha_van_der_merwe": {
        "name": "Natasha Van Der Merwe",
        "tagline": "The Holistic Performance Coach",
        "description": "South African coach known for holistic approach. Coached multiple Ironman champions. Emphasizes work-life balance, athlete-centered coaching, and addressing the whole athlete (physical, mental, nutritional).",
        "philosophy": """Natasha Van Der Merwe's Holistic Coaching Philosophy:
        
• ATHLETE-CENTERED: Coaching adapts to athlete's life, not vice versa
• HOLISTIC APPROACH: Address physical, mental, emotional, and nutritional needs
• COMMUNICATION: Regular dialogue, athlete input into training decisions
• WORK-LIFE BALANCE: Sustainable training that fits real-world constraints
• INDIVIDUAL DIFFERENCES: No cookie-cutter plans, personalized approach
• RECOVERY EMPHASIS: Recovery is part of training, not separate
• NUTRITION INTEGRATION: Proper fueling is non-negotiable
• MENTAL STRENGTH: Confidence building through progressive success
• LONG-TERM DEVELOPMENT: Build athletes over years, not months""",
        
        "training_distribution": {
            "typical_week": "Swim 18%, Bike 42%, Run 30%, Strength/Mobility 10%",
            "base_phase": "Lower intensity, higher volume, skills development",
            "build_phase": "Maintain volume, add structured intensity",
            "peak_phase": "Race-specific, practice execution, maintain freshness"
        },
        
        "key_workouts": [
            "Long aerobic rides - 4-6 hours at comfortable pace",
            "Progressive run - start easy, finish at marathon pace",
            "Swim technique sessions - drills and form focus",
            "Tempo intervals - sustained efforts at threshold",
            "Brick workouts - teach bike-to-run transition",
            "Recovery sessions - truly easy, active recovery",
            "Race-pace practice - practice nutrition and pacing"
        ],
        
        "periodization_structure": {
            "off_season": "4-6 weeks: Unstructured, fun training, recharge",
            "base_phase": "8-12 weeks: Build aerobic foundation",
            "build_phase": "8-12 weeks: Add intensity progressively",
            "race_phase": "6-8 weeks: Race-specific, sharpen fitness",
            "taper": "2-3 weeks: Reduce volume, maintain quality"
        },
        
        "recovery_strategy": "Recovery is individualized. Listen to body, adjust training when fatigued. Sleep, nutrition, and stress management are priorities. Recovery weeks every 3-4 weeks.",
        
        "special_emphasis": [
            "Training must fit YOUR life, not the other way around",
            "Communication with coach is essential",
            "Recovery is when adaptation happens",
            "Nutrition must support training load",
            "Mental preparation is as important as physical",
            "Progress over perfection - don't stress missed workouts",
            "Build confidence through achievable progressive goals",
            "Sustainable training prevents burnout",
            "Address the WHOLE athlete, not just fitness"
        ]
    },
    
    # 13. BJÖRN GEESMANN - German Precision & Volume
    "bjoern_geesmann": {
        "name": "Björn Geesmann",
        "tagline": "The German Volume Master",
        "description": "German coach known for high-volume training approach. Coached multiple European champions. Emphasizes consistent high volume, structured periodization, and meticulous attention to detail.",
        "philosophy": """Björn Geesmann's Volume-Based Philosophy:
        
• HIGH VOLUME: Build capacity through consistent high training loads
• STRUCTURED APPROACH: Everything is planned, measured, and analyzed
• CONSISTENCY: Regular training over months/years builds champions
• GERMAN EFFICIENCY: Systematic progression, no wasted efforts
• BASE BUILDING: Massive aerobic base before intensity
• TECHNICAL EXCELLENCE: Perfect form in all three sports
• PROGRESSIVE OVERLOAD: Gradual, systematic volume increases
• RECOVERY INTEGRATION: High volume requires structured recovery
• DATA ANALYSIS: Track everything, analyze trends, adjust accordingly""",
        
        "training_distribution": {
            "base_phase": "Very high volume - 20-30 hours/week for elites",
            "intensity_distribution": "75% Zone 1-2, 15% Zone 3-4, 10% Zone 5",
            "sport_balance": "Swim 20%, Bike 45%, Run 35%",
            "peak_phase": "Maintain volume, increase race-pace work"
        },
        
        "key_workouts": [
            "Long rides - 6-8 hours steady aerobic pace",
            "Long runs - 2.5-3 hours easy to moderate pace",
            "Swim endurance - 4000-5000m continuous swimming",
            "Tempo sets - sustained threshold efforts (swim/bike/run)",
            "Brick workouts - long bike followed by run",
            "Double days - AM and PM sessions to increase volume",
            "Recovery sessions - short, very easy efforts"
        ],
        
        "periodization_structure": {
            "base_phase": "12-16 weeks: Build massive volume",
            "intensity_phase": "8-10 weeks: Add structured intervals",
            "race_prep": "6-8 weeks: Race-specific intensity",
            "taper": "2-3 weeks: Reduce volume, keep intensity"
        },
        
        "recovery_strategy": "Recovery weeks every 3-4 weeks with 30% volume reduction. Massage, compression, nutrition protocols. Active recovery sessions included.",
        
        "special_emphasis": [
            "Volume builds the engine - consistency is key",
            "Track ALL training metrics (distance, time, HR, power)",
            "Base phase cannot be rushed - takes months",
            "Technical efficiency saves energy over long races",
            "Nutrition must match training load (high carb)",
            "Sleep 8-9 hours minimum with high volume",
            "Double days allow more volume without injury",
            "Progressive overload - increase 10% every 3 weeks",
            "German discipline - stick to the plan"
        ]
    },
    
    # 14. ANDY POTTS - Pro Experience & Racing Strategy
    "andy_potts": {
        "name": "Andy Potts",
        "tagline": "The Pro Racing Strategist",
        "description": "Former professional triathlete turned coach. Knows what it takes to compete at the highest level. Emphasizes race execution, strategic training, and mental toughness from years of pro racing experience.",
        "philosophy": """Andy Potts' Pro Racing Philosophy:
        
• RACE EXECUTION: Training must prepare you to RACE, not just finish
• MENTAL TOUGHNESS: Champions are made in tough workouts
• STRATEGIC TRAINING: Quality over junk miles
• BIKE POWER: Strong cycling creates opportunities in triathlon
• EFFICIENT SWIMMING: Swim technique and drafting skills
• RUN OFF THE BIKE: Practice running tired, it's race reality
• RACING IS DIFFERENT: Train to race, not just train
• COMPETITIVE MINDSET: Embrace discomfort, push limits
• PRO INSIGHTS: Learn from elite racing strategies""",
        
        "training_distribution": {
            "swim_focus": "15% - technique and speed, not just volume",
            "bike_focus": "45% - power development and race-pace riding",
            "run_focus": "30% - brick runs and race-pace work",
            "other": "10% - strength, mobility, skills"
        },
        
        "key_workouts": [
            "Bike power intervals - 8-10x5min at 110-120% FTP",
            "Race-pace bike - 3-4 hours at target race watts",
            "Brick runs - bike hard, then run at race pace tired",
            "Swim speed sets - 20x50m at race pace + 10sec",
            "Tempo run - 45-60min at half-marathon pace",
            "Open water swim - practice sighting and drafting",
            "Race simulation - practice transitions and pacing"
        ],
        
        "periodization_structure": {
            "off_season": "4 weeks: Rest, fun, recharge",
            "base_building": "6-8 weeks: Build fitness foundation",
            "intensity_phase": "8-10 weeks: Develop race speed",
            "race_specific": "6-8 weeks: Sharpen and practice execution",
            "taper": "10-14 days: Quick, sharp taper"
        },
        
        "recovery_strategy": "Strategic recovery - easy days truly easy, hard days truly hard. Recovery sessions are part of the plan, not optional. Listen to body but don't be soft.",
        
        "special_emphasis": [
            "Train like a PRO even if you're not one",
            "Race execution is a skill - practice it",
            "Bike power separates good from great",
            "Practice running off the bike - it's different",
            "Open water skills matter - practice them",
            "Mental toughness wins close races",
            "Embrace discomfort in key workouts",
            "Racing is about pushing limits, not comfort",
            "Learn race strategy - when to push, when to hold"
        ]
    },
    
    # 15. NORWEGIAN METHOD - Self-Coached Champions
    "norwegian_method": {
        "name": "Norwegian Method",
        "tagline": "The Self-Coached Champions Approach",
        "description": "Training methodology of Norwegian triathletes Kristian Blummenfelt, Gustav Iden, and Casper Stornes. Self-coached athletes who've dominated Olympic and Ironman racing through innovative training methods, double threshold sessions, and scientific experimentation.",
        "philosophy": """Norwegian Method Training Philosophy:
        
• DOUBLE THRESHOLD: Two threshold sessions per day (revolutionary approach)
• HIGH INTENSITY: More high-intensity work than traditional 80/20
• SCIENTIFIC APPROACH: Self-experimentation and data analysis
• ALTITUDE TRAINING: Strategic use of altitude camps
• HEAT ADAPTATION: Indoor training in extreme heat
• INNOVATIVE METHODS: Challenge conventional wisdom
• THRESHOLD FOCUS: Develop ability to sustain race pace
• BRICK THRESHOLD: Bike threshold immediately followed by run threshold
• MENTAL TOUGHNESS: Embrace suffering, push boundaries""",
        
        "training_distribution": {
            "intensity_distribution": "65% Zone 1-2, 35% Zone 3-5 (higher intensity than traditional)",
            "double_threshold_days": "2-3x per week: AM and PM threshold sessions",
            "typical_week": "High intensity Tuesday, Wednesday, Friday with easy days between",
            "sport_balance": "Swim 15%, Bike 45%, Run 35%, Cross-training 5%"
        },
        
        "key_workouts": [
            "Double threshold - AM: 40min bike threshold, PM: 30min run threshold",
            "4x8min intervals at 95-100% FTP (bike or run)",
            "Brick threshold - 60min bike threshold + 30min run threshold",
            "Race-pace simulation - practice Olympic/Ironman race intensity",
            "Heat chamber training - indoor bike/run in 35-40°C heat",
            "Altitude training blocks - 3-4 weeks at 2000-2500m",
            "Recovery sessions - very easy, active recovery"
        ],
        
        "periodization_structure": {
            "base_phase": "6-8 weeks: Build volume, limited intensity",
            "double_threshold_phase": "10-12 weeks: Implement double sessions",
            "race_specific": "6-8 weeks: Practice race pace and intensity",
            "altitude_camps": "2-3 camps per year (3-4 weeks each)",
            "taper": "7-10 days: Short, sharp taper"
        },
        
        "recovery_strategy": "Strategic recovery - easy days are truly easy (Zone 1 only). Hard days have double sessions. Recovery weeks every 3-4 weeks. Listen to HRV and fatigue markers.",
        
        "special_emphasis": [
            "DOUBLE THRESHOLD is revolutionary but demanding",
            "Not for beginners - requires solid aerobic base first",
            "Higher injury risk - must monitor fatigue closely",
            "Heat adaptation improves performance significantly",
            "Altitude training boosts aerobic capacity",
            "Scientific approach - track metrics, experiment",
            "Threshold development is race-winning fitness",
            "Mental toughness separates good from great",
            "Challenge conventional training wisdom",
            "Self-awareness is critical - know your limits"
        ]
    },
    
    # 16. JOEL FILIOL - Science-Based Triathlon
    "joel_filiol": {
        "name": "Joel Filiol",
        "tagline": "The Science-Based Triathlon Coach",
        "description": "Canadian coach and exercise physiologist. Former coach of Simon Whitfield (Olympic Gold). Known for scientific, evidence-based approach to triathlon training with focus on physiological testing and individualization.",
        "philosophy": """Joel Filiol's Science-Based Philosophy:
        
• EVIDENCE-BASED: Training grounded in exercise science research
• PHYSIOLOGICAL TESTING: Regular lab testing to guide training zones
• INDIVIDUALIZATION: Every athlete responds differently
• LACTATE THRESHOLD: Focus on improving threshold power/pace
• PERIODIZATION: Classic periodization with clear phases
• RECOVERY SCIENCE: Evidence-based recovery protocols
• TECHNIQUE OPTIMIZATION: Biomechanical efficiency in all sports
• DATA-DRIVEN: Use metrics to guide training decisions
• LONG-TERM DEVELOPMENT: Build athletes systematically over years""",
        
        "training_distribution": {
            "intensity_distribution": "75% Zone 1-2, 15% Zone 3-4, 10% Zone 5",
            "sport_balance": "Swim 18%, Bike 42%, Run 32%, Strength 8%",
            "weekly_structure": "2-3 hard sessions, 4-5 easy sessions, 1 rest day",
            "periodization": "Classic linear periodization with testing blocks"
        },
        
        "key_workouts": [
            "Lactate threshold test - lab or field test every 6-8 weeks",
            "Threshold intervals - 4-6x8min at LT1/LT2",
            "VO2max intervals - 5-8x3min at maximal aerobic power",
            "Long aerobic sessions - 2-4 hours Zone 2",
            "Technique drills - all three sports, weekly",
            "Brick workouts - bike-to-run transition practice",
            "Race-pace rehearsals - practice race intensity"
        ],
        
        "periodization_structure": {
            "base_phase": "8-12 weeks: Aerobic development, technique",
            "build_phase": "8-10 weeks: Lactate threshold development",
            "intensity_phase": "6-8 weeks: VO2max and race pace",
            "peak_phase": "4-6 weeks: Race-specific sharpening",
            "taper": "2-3 weeks: Volume reduction, maintain intensity",
            "testing": "Every 6-8 weeks: Reassess zones"
        },
        
        "recovery_strategy": "Evidence-based recovery: sleep optimization, nutrition timing, active recovery protocols. HRV monitoring to adjust training. Recovery weeks every 4th week.",
        
        "special_emphasis": [
            "Physiological testing drives training zones",
            "Individual response varies - adjust accordingly",
            "Lactate threshold is most important marker",
            "Technique efficiency = free speed",
            "Recovery is part of the training prescription",
            "Data guides decisions, not guesswork",
            "Long-term athlete development over quick fixes",
            "Testing every 6-8 weeks to update zones",
            "Science-based doesn't mean complicated"
        ]
    },
    
    # 17. DAVID TILBURY-DAVIS - Pragmatic Performance
    "david_tilbury_davis": {
        "name": "David Tilbury-Davis",
        "tagline": "The Pragmatic Performance Coach",
        "description": "British coach with pragmatic, results-focused approach. Known for working with age-group athletes and balancing elite training principles with real-world constraints. Emphasizes efficiency and smart training.",
        "philosophy": """David Tilbury-Davis' Pragmatic Philosophy:
        
• SMART TRAINING: Maximum results from available training time
• EFFICIENCY FOCUS: Every workout has clear purpose
• REALISTIC APPROACH: Balance training with work/family life
• KEY SESSIONS: Protect the important workouts
• FLEXIBILITY: Adapt plan to real-world challenges
• PROGRESSIVE LOADING: Systematic build-up over time
• RECOVERY REALISM: Can't train hard if not recovered
• TECHNIQUE MATTERS: Efficiency saves energy in races
• RESULTS-ORIENTED: Focus on what works for YOU""",
        
        "training_distribution": {
            "time_crunched": "8-12 hours/week for age-groupers",
            "key_sessions": "2-3 hard sessions per week (non-negotiable)",
            "filler_sessions": "Easy aerobic work, flexible timing",
            "intensity": "70% easy, 20% moderate, 10% hard"
        },
        
        "key_workouts": [
            "Key session 1: Bike intervals (threshold or VO2max)",
            "Key session 2: Run intervals (threshold or race pace)",
            "Key session 3: Brick or long ride",
            "Swim technique - 2-3x per week, focus on efficiency",
            "Easy runs - aerobic maintenance",
            "Recovery rides - active recovery",
            "Long weekend session - bike or run, build endurance"
        ],
        
        "periodization_structure": {
            "base_phase": "6-8 weeks: Build aerobic base",
            "build_phase": "6-8 weeks: Add key interval sessions",
            "specific_phase": "4-6 weeks: Race-specific work",
            "taper": "10-14 days: Reduce volume, keep quality",
            "flexibility": "Adjust based on life demands"
        },
        
        "recovery_strategy": "Prioritize key sessions - if tired, skip filler work not key sessions. Sleep and nutrition are non-negotiable. Life stress counts as training stress.",
        
        "special_emphasis": [
            "Protect KEY sessions - these drive adaptation",
            "Filler sessions are flexible - adapt to energy levels",
            "Consistency beats perfection",
            "Life stress affects training - adjust accordingly",
            "Efficiency in training AND technique",
            "Work smarter, not just harder",
            "Real world constraints are OK - work with them",
            "Progress tracking shows what works for YOU",
            "Sustainable training prevents burnout"
        ]
    },
    
    # 18. BEN RESZEL - The Multi-Sport Performance Coach
    "ben_reszel": {
        "name": "Ben Reszel",
        "tagline": "The Multi-Sport Performance Coach",
        "description": "Australian coach and former professional triathlete. Known for balanced multi-sport development, technical swimming focus, and sustainable high-performance training for both professionals and age-groupers.",
        "philosophy": """Ben Reszel's Multi-Sport Performance Philosophy:
        
• BALANCED DEVELOPMENT: Equal focus on swim, bike, run - no weak links
• TECHNICAL SWIMMING: Swimming technique is the biggest differentiator
• SUSTAINABLE INTENSITY: High performance through smart training, not just volume
• ATHLETE EMPOWERMENT: Teach athletes to understand their training
• ADAPTABILITY: Training must adapt to athlete's response
• RACE EXECUTION: Practice racing skills in training
• PROGRESSIVE BUILD: Gradual, sustainable progression over seasons
• RECOVERY INTEGRATION: Recovery is part of the training prescription
• HOLISTIC APPROACH: Address all aspects of performance""",
        
        "training_distribution": {
            "typical_week": "Swim 20%, Bike 40%, Run 30%, Strength/Skills 10%",
            "intensity_distribution": "70% Zone 1-2, 20% Zone 3-4, 10% Zone 5",
            "base_phase": "Higher volume, technical focus, build aerobic base",
            "race_phase": "Maintain volume, increase race-specific work"
        },
        
        "key_workouts": [
            "Swim technique sessions - drills, video analysis, stroke efficiency",
            "Bike threshold sets - 3-4x12min at FTP",
            "Run tempo - 40-60min at half-marathon pace",
            "Brick workouts - bike-to-run transition practice",
            "Race-pace rehearsals - practice nutrition and pacing",
            "Open water skills - drafting, sighting, navigation",
            "Long aerobic sessions - 3-6 hours on bike, 90min-2.5hr run"
        ],
        
        "periodization_structure": {
            "off_season": "4-6 weeks: Active recovery, fun training",
            "base_phase": "10-14 weeks: Build volume, technical work",
            "build_phase": "8-10 weeks: Add intensity, maintain volume",
            "race_specific": "6-8 weeks: Sharpen fitness, practice execution",
            "taper": "14-18 days: Reduce volume 40-50%, keep race pace"
        },
        
        "recovery_strategy": "Strategic recovery weeks every 3-4 weeks. Monitor training stress and fatigue. Recovery sessions are prescribed, not optional. Sleep and nutrition non-negotiable.",
        
        "special_emphasis": [
            "Swimming technique = free speed in races",
            "Don't neglect the swim - it's your first impression",
            "Balanced multi-sport athlete beats specialists",
            "Practice transitions and race skills weekly",
            "Understand WHY you're doing each workout",
            "Training should be sustainable year-round",
            "Race execution is a trainable skill",
            "Recovery allows adaptation to happen",
            "Progressive build over seasons, not weeks"
        ]
    },
    
    # 19. AI SUPER TRAINER - The Evidence-Based Performance Optimizer
    "ai_super_trainer": {
        "name": "AI Super Trainer",
        "tagline": "The Evidence-Based Performance Optimizer",
        "description": "AI-synthesized coaching methodology combining cutting-edge sports science with proven elite training principles. Integrates polarized training, periodization science, data-driven precision, holistic athlete development, and race-specific preparation into a comprehensive modern triathlon training system.",
        "philosophy": """AI Super Trainer's Integrated Performance Philosophy:

🔬 EVIDENCE-BASED FOUNDATION (Seiler + Filiol + Fitzgerald)
• POLARIZED DISTRIBUTION: 75-80% Zone 1-2, <5% Zone 3, 15-20% Zone 4-5
• SCIENTIFIC TESTING: Regular threshold testing (every 6-8 weeks) to update zones
• DATA-DRIVEN DECISIONS: Track HRV, sleep, training load (TSS/CTL/ATL/TSB)
• 80/20 PRINCIPLE: High volume of easy aerobic work prevents overtraining
• INDIVIDUALIZATION: Every athlete responds differently - adjust accordingly

⚡ ADVANCED INTENSITY TECHNIQUES (Norwegian Method + Andy Potts)
• STRATEGIC DOUBLE THRESHOLD: 1-2x per week in build phase (AM bike, PM run)
• RACE-SPECIFIC INTENSITY: Practice race pace regularly, not just base training
• THRESHOLD DEVELOPMENT: Build sustainable power/pace at lactate threshold
• BRICK THRESHOLD SESSIONS: Bike threshold → immediate run threshold
• MENTAL TOUGHNESS: Embrace discomfort in key sessions, build racing confidence

🎯 PRECISION & EXECUTION (Dan Lorang + Greg McMillan)
• POWER-BASED CYCLING: Train with power meter, not just heart rate
• PACE-BASED RUNNING: Use pace zones for race-specific training
• MEASURABLE TARGETS: Every workout has specific metrics and outcomes
• RACE SIMULATION: Practice race conditions (nutrition, pacing, transitions)
• MARGINAL GAINS: Optimize equipment, nutrition, recovery protocols

🏊 MULTI-SPORT MASTERY (Ben Reszel + Dave Scott)
• SWIM TECHNIQUE PRIORITY: Efficiency = free speed (weekly technique work)
• BIKE VOLUME EMPHASIS: Cycling is the Ironman differentiator (45-50% of training)
• RUN OFF THE BIKE: Weekly brick workouts teach run-when-fatigued skill
• BALANCED DEVELOPMENT: No weak links - address all three disciplines
• TRANSITION SKILLS: Practice T1/T2 weekly during race-specific phase

📊 STRUCTURED PERIODIZATION (Joe Friel + Renato Canova)
• CLASSIC PHASES: Base (12 weeks) → Build (10 weeks) → Peak (6 weeks) → Taper (2-3 weeks)
• PROGRESSIVE OVERLOAD: Systematic volume/intensity increases (3 weeks up, 1 week recovery)
• TSS-BASED PLANNING: Target weekly TSS progression with CTL ramp rate <8/week
• RACE-SPECIFIC BLOCKS: Final 6 weeks = race-pace work + execution practice
• PROPER TAPER: 14-21 day taper with 40-60% volume reduction, maintain intensity sharpness

🧘 HOLISTIC ATHLETE CARE (Natasha Van Der Merwe + Phil Maffetone)
• RECOVERY SCIENCE: Sleep 8+ hours, HRV monitoring, compression, massage
• NUTRITION TIMING: Fuel workouts properly, practice race nutrition
• STRESS MANAGEMENT: Training + life stress = total stress (adjust when needed)
• INJURY PREVENTION: Strength training 2x/week, mobility work, proper progression
• LONG-TERM DEVELOPMENT: Build fitness over years, not weeks (sustainable)

🎓 ATHLETE EDUCATION (Brad Hudson + Joel Filiol)
• UNDERSTAND WHY: Athletes learn physiological purpose of each workout
• ADAPTIVE INTELLIGENCE: Adjust training based on daily readiness/fatigue
• SELF-AWARENESS: Recognize signs of overtraining, under-recovery
• PROGRESSIVE AUTONOMY: Develop ability to make smart training decisions
• CONTINUOUS LEARNING: Regular testing provides feedback on progress

🏁 RACE OPTIMIZATION (Andy Potts + Dave Scott + Dan Lorang)
• PRACTICE EXECUTION: Race-pace work weekly in race-specific phase
• HEAT ADAPTATION: Indoor training in hot conditions if racing in heat
• ALTITUDE CAMPS: Strategic use of altitude for aerobic development (optional)
• PACING STRATEGY: Learn when to push, when to hold back in races
• TRANSITION MASTERY: Fast, efficient T1/T2 saves minutes

🔄 RECOVERY INTEGRATION (All Coaches)
• STRATEGIC RECOVERY: Easy days truly easy (Zone 1 only), hard days truly hard
• RECOVERY WEEKS: Every 4th week = 30-40% volume reduction
• ACTIVE RECOVERY: Easy swimming, yoga, walking on rest days
• MONITORING: HRV, resting HR, sleep quality, subjective fatigue
• PERIODIZED REST: More recovery as intensity increases""",
        
        "training_distribution": {
            "base_phase": "Swim 18%, Bike 48%, Run 28%, Strength 6% | 80% Zone 1-2, 10% Zone 3-4, 10% Zone 5",
            "build_phase": "Swim 16%, Bike 46%, Run 30%, Brick 8% | 75% Zone 1-2, 10% Zone 3-4, 15% Zone 5",
            "peak_phase": "Swim 14%, Bike 48%, Run 30%, Race-specific 8% | 70% Zone 1-2, 10% Zone 3-4, 20% Zone 5",
            "weekly_structure": "2-3 KEY sessions (hard), 4-5 SUPPORTING sessions (easy/moderate), 1 complete rest day",
            "intensity_philosophy": "Polarized distribution - most work very easy, targeted work very hard, minimal gray zone"
        },
        
        "key_workouts": [
            "Threshold Testing - FTP test (bike), threshold pace test (run), CSS test (swim) every 6-8 weeks",
            "Double Threshold - AM: 40-60min bike at FTP, PM: 30-40min run at threshold (1-2x/week in build)",
            "Long Polarized Ride - 4-7 hours mostly Zone 1-2 with 2-3x20min at race pace",
            "Brick Threshold - 90-120min bike at FTP + 30-45min run at threshold pace",
            "Swim Technique + CSS - 30min drills + 6-10x100m at critical swim speed",
            "VO2max Intervals - 5-8x3-5min at max aerobic power (Zone 5) with equal rest",
            "Race Simulation - Practice full race-day execution: nutrition, pacing, transitions",
            "Recovery Sessions - Zone 1 only, 45-90min, active recovery (truly easy)",
            "Strength & Mobility - 2x45min strength circuits + daily 15min mobility/yoga"
        ],
        
        "periodization_structure": {
            "off_season": "4-6 weeks: Unstructured fun training, mental refresh, address weaknesses",
            "base_phase": "12-16 weeks: Build massive aerobic base, high volume Zone 1-2, swim technique emphasis",
            "build_phase": "8-12 weeks: Add polarized intensity (2-3 hard sessions/week), maintain volume, introduce threshold work",
            "peak_phase": "6-8 weeks: Race-specific intensity, practice execution, 2x VO2max + 2x threshold/week",
            "race_specific": "Final 3 weeks: Tune sharpness, reduce volume 20%, practice race-day logistics",
            "taper": "14-21 days: Reduce volume 40-60%, maintain intensity with short intervals, prioritize sleep",
            "recovery_blocks": "Every 4th week: Reduce volume 30-40%, maintain easy sessions only"
        },
        
        "recovery_strategy": """Evidence-Based Recovery Protocol:
        
DAILY MONITORING:
• Resting heart rate (should be within 5 bpm of baseline)
• HRV score (use app like HRV4Training or Whoop)
• Sleep quality and duration (target 8+ hours)
• Subjective fatigue (1-10 scale)
• Muscle soreness (DOMS)

RECOVERY INTERVENTIONS:
• Sleep optimization: Dark room, cool temp, consistent schedule
• Compression garments: Immediately post-workout for 2-3 hours
• Massage/foam rolling: 2x per week, focus on problem areas
• Ice baths: After very hard sessions (10-15min at 10-15°C)
• Active recovery: Easy Zone 1 swimming on rest days
• Nutrition: High carb during training, adequate protein (1.6-2.2g/kg)

ADJUSTMENT RULES:
• If HRV drops >10% for 2+ days → reduce intensity, add rest day
• If resting HR elevated 5+ bpm → skip hard session, do easy Zone 1
• If sleep quality poor 2+ nights → adjust training volume
• If cumulative fatigue high → bring recovery week forward
• If TSB (form) drops below -30 → mandatory recovery week

PERIODIZED RECOVERY:
• Base phase: 1 rest day/week, recovery weeks every 4 weeks
• Build phase: 1 rest day/week, recovery weeks every 3-4 weeks
• Peak phase: 1-2 rest days/week, extra recovery due to high intensity
• Life stress counts: Adjust training if work/personal stress high""",
        
        "special_emphasis": [
            "🔬 SCIENCE-BASED: All training principles grounded in peer-reviewed research",
            "⚡ POLARIZED INTENSITY: Avoid gray zone (Zone 3) - go very easy or very hard",
            "📊 DATA-DRIVEN: Use power meter, pace zones, HRV - not just feel",
            "🎯 RACE-SPECIFIC: Final 6 weeks = practice race execution weekly",
            "🏊 SWIM TECHNIQUE: Efficiency > volume - weekly technique work required",
            "🚴 BIKE EMPHASIS: Cycling wins Ironman races - 45-50% of training time",
            "🏃 BRICK MASTERY: Weekly brick workouts teach run-when-fatigued skill",
            "💪 STRENGTH WORK: 2x/week year-round prevents injury, builds durability",
            "😴 RECOVERY PRIORITY: Adaptation happens during recovery, not training",
            "🧠 MENTAL SKILLS: Visualization, race-scenario rehearsal, confidence building",
            "🍎 NUTRITION SCIENCE: Fuel workouts properly, practice race nutrition EXACTLY",
            "🌡️ ENVIRONMENTAL: Heat/altitude adaptation if racing in extreme conditions",
            "📈 PROGRESSIVE OVERLOAD: Increase load systematically, never >10% per week",
            "🔄 PERIODIZATION: Respect base→build→peak→taper phases (no shortcuts)",
            "⚠️ DOUBLE THRESHOLD: Advanced technique - requires solid aerobic base first",
            "🧘 HOLISTIC ATHLETE: Address sleep, stress, nutrition, relationships, not just training",
            "🎓 ATHLETE EDUCATION: Understand WHY behind each workout",
            "🔁 ADAPTIVE TRAINING: Adjust based on daily readiness, not rigid plan",
            "🏁 EXECUTION PRACTICE: Race skills are trainable - practice weekly",
            "📉 PROPER TAPER: 14-21 days, trust the training, arrive fresh"
        ]
    }
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TRAINER STYLE HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_all_trainer_styles() -> List[Dict[str, Any]]:
    """Get list of all trainer styles with basic info."""
    return [
        {
            "id": key,
            "name": style["name"],
            "tagline": style["tagline"],
            "description": style["description"]
        }
        for key, style in TRAINER_STYLES.items()
    ]


def get_trainer_style(style_id: str) -> Dict[str, Any]:
    """Get complete trainer style configuration."""
    return TRAINER_STYLES.get(style_id, TRAINER_STYLES["joe_friel"])  # Default to Joe Friel


def build_trainer_specific_prompt(style_id: str) -> str:
    """Build the trainer-specific section of the training prompt."""
    style = get_trainer_style(style_id)
    
    prompt = f"""
━━━ TRAINER METHODOLOGY: {style['name'].upper()} ━━━

{style['philosophy']}

━━━ INTENSITY DISTRIBUTION ━━━
"""
    
    for phase, distribution in style['training_distribution'].items():
        prompt += f"  • {phase.replace('_', ' ').title()}: {distribution}\n"
    
    prompt += "\n━━━ KEY WORKOUT TYPES ━━━\n"
    for i, workout in enumerate(style['key_workouts'], 1):
        prompt += f"  {i}. {workout}\n"
    
    prompt += "\n━━━ PERIODIZATION STRUCTURE ━━━\n"
    for phase, description in style['periodization_structure'].items():
        prompt += f"  • {phase.replace('_', ' ').title()}: {description}\n"
    
    prompt += f"\n━━━ RECOVERY STRATEGY ━━━\n  {style['recovery_strategy']}\n"
    
    prompt += "\n━━━ SPECIAL EMPHASIS ━━━\n"
    for emphasis in style['special_emphasis']:
        prompt += f"  ⚠️  {emphasis}\n"
    
    return prompt


def get_detailed_workout_instructions() -> str:
    """Return detailed instructions for generating comprehensive workout details."""
    return """
━━━ DETAILED WORKOUT REQUIREMENTS ━━━

⚠️  CRITICAL: Every workout MUST include comprehensive details!

REQUIRED WORKOUT STRUCTURE:
{{
  "date": "YYYY-MM-DD",
  "title": "Descriptive title (e.g., 'Threshold Intervals', 'Easy Recovery Run')",
  "sportType": "running/cycling/swimming/strength/triathlon",
  "workoutType": "easy/tempo/interval/long/recovery/race",
  "durationMinutes": <number>,
  "targetTSS": <number>,
  "intensityZone": "zone1/zone2/zone3/zone4/zone5",
  "description": "COMPREHENSIVE workout description (see below)"
}}

━━━ WORKOUT DESCRIPTION FORMAT ━━━

The "description" field MUST be detailed and include:

1. WARMUP (always include):
   - Duration and intensity
   - Example: "10min easy warmup in Zone 1"

2. MAIN WORK (be specific):
   For INTERVALS:
   - Number of repetitions
   - Duration of each interval
   - Target pace/power/HR zone
   - Recovery duration and type
   - Example: "5x1000m at threshold pace (Zone 4) with 2min easy jog recovery"
   
   For TEMPO:
   - Duration at tempo effort
   - Target pace/power/HR range
   - Example: "20min continuous tempo effort at Zone 3 (half-marathon pace)"
   
   For LONG RUNS:
   - Total duration/distance
   - Any pace variations
   - Example: "90min easy run in Zone 2, last 15min at marathon pace"
   
   For EASY/RECOVERY:
   - Emphasis on easy effort
   - Example: "45min easy recovery run, Zone 1-2, conversational pace"

3. COOLDOWN (always include):
   - Duration and intensity
   - Example: "10min easy cooldown in Zone 1"

4. ADDITIONAL NOTES (when relevant):
   - Specific focus (form, cadence, nutrition)
   - Special instructions
   - Example: "Focus on maintaining cadence >170spm. Practice race nutrition."

━━━ COMPLETE WORKOUT EXAMPLES ━━━

Example 1 - Interval Workout:
{{
  "title": "VO2max Intervals",
  "description": "Warmup: 15min easy running in Zone 1-2 with 3x100m strides. Main: 6x800m at VO2max pace (Zone 5, ~5K race pace) with 400m easy jog recovery between intervals. Focus on maintaining consistent pace across all intervals. Cooldown: 10min easy running in Zone 1. Total: 60min"
}}

Example 2 - Long Run:
{{
  "title": "Progressive Long Run",
  "description": "90min long run starting in Zone 2. Run first 60min at comfortable aerobic pace, then increase to marathon pace (Zone 3) for 20min, finish with 10min easy cooldown in Zone 1. Practice race-day nutrition (gel at 45min and 75min). Focus on maintaining form as fatigue sets in."
}}

Example 3 - Tempo Run:
{{
  "title": "Sustained Tempo",
  "description": "Warmup: 10min easy running in Zone 1. Main: 30min continuous tempo effort at Zone 3 (half-marathon pace, comfortably hard). Focus on relaxed form and controlled breathing. Cooldown: 10min easy in Zone 1 with light stretching. Total: 50min"
}}

Example 4 - Easy Recovery:
{{
  "title": "Easy Recovery Run",
  "description": "45min easy recovery run at Zone 1-2. Pace should feel comfortable and conversational. If HR rises above Zone 2, slow down. This is active recovery - do NOT push pace. Focus on relaxed form and enjoying the run."
}}

━━━ TAPER PHASE WORKOUTS ━━━

Taper workouts MUST:
- Reduce volume by 50-70%
- Maintain intensity in short bursts
- Include race-pace efforts
- Example: "30min easy run with 3x5min at race pace, 2min recovery between"

━━━ BRICK WORKOUTS (Triathlon) ━━━

Brick workouts MUST specify:
- Bike duration and intensity
- Transition
- Run duration and intensity
- Example: "90min bike at Zone 2-3, quick transition (practice race setup), 30min run starting at Zone 3 (expect heavy legs first 10min)"

━━━ RACE-SPECIFIC WORKOUTS ━━━

Race simulation workouts MUST:
- Mimic race conditions (time of day, terrain, weather considerations)
- Practice pacing strategy
- Test race nutrition
- Example: "20K run: First 5K at easy pace, then 10K at goal marathon pace, final 5K push to half-marathon pace. Practice fueling: gel at 30min and 60min."
"""
