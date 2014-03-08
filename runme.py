import os, shutil, sys
import traceback
import re
import codecs # Why the hell we are still stuck with cp1252? This is a 2012 game, hey!
import random

try:
    # Though something with argparse could be more friendly for *NIXers, this is meant to be cross-platform. So we do an interactive wizard.

    print("Enter the path to your mod: ")
    path = sys.stdin.readline().strip()

    # TODO: Finish this feature if people are asking for it.

    #print("Do you want to keep existing retinues? (Y/N): ")
    #keepExist = sys.stdin.readline().strip().lower()
    #if keepExist == 'y':
    #    print ("Sorry, this is not currently supported. Please wait for the auther to release a new version...")
    #    exit()

    culturePath = os.path.join(path, "common/cultures")
    cultureFiles = [ f for f in os.listdir(culturePath) if os.path.isfile(os.path.join(culturePath,f)) ]

    cul_to_grp = {}

    for f in cultureFiles:
        fi = codecs.open(os.path.join(culturePath, f), 'rb', 'cp1252')
        content = fi.read()
        fi.close()
        
        # Parse the file for only cultural groups & cultures
        m=re.findall("[a-z_]*_grp = {|[a-z_]*_cul = {", content)

        cur_grp = "default"

        for s in m:
            if (s.endswith("_grp = {")):
                cur_grp = s[:-len("_grp = {")]
            else:
                cur_cul = s[:-len("_cul = {")]
                cul_to_grp[cur_cul] = cur_grp

    if not os.path.exists(os.path.join(path, "common/retinue_subunits/")):
            os.makedirs(os.path.join(path, "common/retinue_subunits/"))
    if not os.path.exists(os.path.join(path, "common/buildings/")):
            os.makedirs(os.path.join(path, "common/buildings/"))
    if not os.path.exists(os.path.join(path, "localisation/")):
            os.makedirs(os.path.join(path, "localisation/"))

    # Named 01 so we are sure they are loaded after the system ones
    ret_out = open(os.path.join(path, "common/retinue_subunits/01_NewCultureRetinues.txt"), "w")
    bld_out = open(os.path.join(path, "common/buildings/01_NewCultures.txt"), "w")
    loc_out = open(os.path.join(path, "localisation/NewCultureBuildings.csv"), "w")
    bld_out.write ("castle = {\n")

    troop_types = ["light_infantry", "heavy_infantry", "pikemen", "light_cavalry",
            "knights", "archers", "horse_archers"]
    bonus_postfix = ["offensive", "defensive", "morale"]
    cost = [1, 2, 2, 2, 4, 1, 2]
    skirmish = [3, 5, 6]
    melee = [1, 2, 4]
    mounted = [3, 4, 6]

    common_ret_count = 0

    def gen_ret (t1, t2, culture_name):
        if culture_name != None:
            culture_name_desc=culture_name.replace("_"," ").title()

        def write_localized_unit_name (str_name):
            # Invent some names for it.
            if t1 in mounted and (t2 == -1 or t2 in mounted):
                # If both mounted, call it horsemen
                loc_out.write ("{1};{0} Horsemen;{0} Cavaliers;{0} Reiter;;{0} Jinetes;;;;;;;;;x\n".format(culture_name_desc, str_name))
            elif t1 in skirmish and (t2 == -1 or t2 in skirmish):
                # If both skirmishers, call it "skirmishers"
                # Not ready for umlauts (too lazy to handle encoding properly)
                loc_out.write ("{1};{0} Skirmishers;Tirailleurs {0};{0} Schuetzen;;Hostigadores {0};;;;;;;;;x\n".format(culture_name_desc, str_name))
            elif t1 in melee and (t2 == -1 or t2 in melee):
                # If both melee, call it "elites"
                # Again no accent
                loc_out.write ("{1};{0} Elites;Elites {0};{0} Eliten;;Elites {0};;;;;;;;;x\n".format(culture_name_desc, str_name))
            else:
                # I have no idea. Just "warriors" then..
                loc_out.write ("{1};{0} Warriors;Guerriers {0};{0} Krieger;;Guerreros {0};;;;;;;;;x\n".format(culture_name_desc, str_name))

        if culture_name == None:
            common_ret_count += 1
            ret_out.write ("RETTYPE_COMMON_NEW{0} = \n".format(common_ret_count))
            write_localized_unit_name("RETTYPE_COMMON_NEW{0}".format(culture_ret_count))
        else:
            ret_out.write ("RETTYPE_CUL_NEWN_{0} = \n".format(culture_name.upper()))
            write_localized_unit_name("RETTYPE_CUL_NEW_{0}".format(culture_name.upper()))

        ret_out.write("{\n")

        # offensive and defensive boni happen in 43% time, morale 14%
        if t2 != -1:
            bonus1 = random.randint(0, 6) // 3
            bonus2 = random.randint(0, 6) // 3

            # 200, 300, 400
            bonus1_amount = (random.randint(0,2) + 2) * 100
            bonus2_amount = 600 - bonus1_amount
        elif random.randint(1, 10) <= 4:
            # Dual type boni for one troop
            while True:
                bonus1 = random.randint(0, 2)
                bonus1a = random.randint(0, 2)
                if bonus1 == bonus1a:
                    continue
                break
            bonus1_amount = (random.randint(0,2) + 2) * 100
            bonus1a_amount = 600 - bonus1_amount
        else:
            bonus1 = random.randint(0, 6) // 3
            bonus1_amount = 600
            bonus1a_amount = 0

        if t2 == -1:
            amount1 = 500
        else:
            if culture_name == None:
                amount1 = random.randint(1, 4) * 100
                amount2 = 500 - amount1
            else:
                amount1 = random.randint(0, 2) * 50 + 200
                amount2 = 500 - amount1
            
        ret_out.write("    first_type = {0}\n".format(t1))
        ret_out.write("    first_amount = {0}\n".format(amount1))

        if t2 != -1:
            ret_out.write("    second_type = {0}\n".format(t2))
            ret_out.write("    second_amount = {0}\n".format(amount2))

        if culture_name != None:
            ret_out.write("    potential = {\n")
            ret_out.write("        culture = {0}_cul\n".format(culture_name))
            ret_out.write("    }\n")

        ret_out.write("    modifier = {\n")
        ret_out.write("        {0}_{1} = 0.{2:03}\n".format(troop_types[t1], bonus_postfix[bonus1], bonus1_amount))
        if t2 != -1:
            ret_out.write("        {0}_{1} = 0.{2:03}\n".format(troop_types[t2], bonus_postfix[bonus2], bonus2_amount))
        elif bonus1a_amount != 0:
            ret_out.write("        {0}_{1} = 0.{2:03}\n".format(troop_types[t1], bonus_postfix[bonus1a], bonus1a_amount))

        ret_out.write("    }\n")

        ret_out.write("}\n\n")

        if culture_name != None:
            write_localized_unit_name("ca_culture_{0}_new_1_desc".format(culture_name))
            for i in range(1, 5):
                loc_out.write ("ca_culture_{0}_new_{1};{2} Barracks;Caserne de {2};{2} Kaserne;;Cuarteles {2};;;;;;;;;x\n".format(culture_name, i, culture_name_desc))

                bld_out.write ("    ca_culture_{0}_new_{1} = {{\n".format(culture_name, i))
                bld_out.write ("        desc = ca_culture_{0}_new_1_desc\n".format(culture_name))
                bld_out.write ("        potential = {\n")
                bld_out.write ("            FROM = {\n")
                bld_out.write ("                culture = {0}_cul {{\n".format(culture_name))
                bld_out.write ("            }\n")
                bld_out.write ("        }\n")
                bld_out.write ("        trigger = {{ TECH_CASTLE_CONSTRUCTION = {0} }}\n".format(i - 1))
                if i == 1:
                    bld_out.write ("        prerequisites = { ca_wall_2 }\n")
                else:
                    bld_out.write ("         upgrades_from = ca_culture_{0}_new_{1}\n".format(culture_name, i - 1))
                bld_out.write ("        build_cost = {0}\n".format((1+i)*100))
                bld_out.write ("        build_time = {0}\n".format((1+i)*365))

                def troop_amount (t1, i, half):
                    if cost[t1] != 4 or not half:
                        re = (2 + i) * 20 / cost[t1]
                        if half:
                            return re / 2
                        else:
                            return re
                    # Special: instead of the theoretical 7.5/10/12.5/15, we give 5/10/15/15
                    return [None, 5, 10, 15, 15][i]

                bld_out.write ("        {0} = {1}\n".format(troop_types[t1], troop_amount(t1, i, t2 != -1)))
                if t2 == -1 and  bonus1a_amount != 0:
                    bld_out.write ("        {0}_{1} = 0.{2:03}\n".format(troop_types[t1], bonus_postfix[bonus1a], bonus1a_amount / 4))
                bld_out.write ("        {0}_{1} = 0.{2:03}\n".format(troop_types[t1], bonus_postfix[bonus1], bonus1_amount / 4))
                if t2 != -1:
                    bld_out.write ("        {0} = {1}\n".format(troop_types[t2], troop_amount(t2, i, t1)))
                    bld_out.write ("        {0}_{1} = 0.{2:03}\n".format(troop_types[t2], bonus_postfix[bonus2], bonus2_amount / 4))
                bld_out.write ("        ai_creation_factor = {0}\n".format(102-i))
                bld_out.write ("        extra_tech_building_start = 0.8\n")
                bld_out.write ("    }\n")

    # Generate four basic troops.
    # Commented out since we are not ready to parse the base files

    #met = [False] * 6
    #regular_ret = 4
    #for i in range(regular_ret):
    #    while True:
    #        t1 = random.randint(0, 5)
    #        t2 = random.randint(0, 5)
    #        if t1==t2:
    #            continue
    #        met2 = list(met) # Deep copy
    #        met2[t1] = True
    #        met2[t2] = True
    #        if sum(met2) + (regular_ret - i - 1) * 2 < 6:
    #            continue
    #        met = met2
    #        break
    #    gen_ret (t1, t2, None)

    for culture in cul_to_grp:
        if random.randint(1, 10) <= 5:
            # 50% chance to focus on one unit type
            # We also assume 100% HA is overpowered
            t1 = random.randint(0, 5)
            gen_ret (t1, -1, culture)
        else:
            # Or split between two unit types
            while True:
                t1 = random.randint(0, 6)
                t2 = random.randint(0, 6)
                if t1==t2:
                    continue

                # If both are skirmish, 40% chance to reroll
                # Light infantries are in neighter group though
                if t1 in skirmish and t2 in skirmish and random.randint(1, 10) <= 4:
                    continue
                # If both are melee, 70% chance to reroll
                if t1 in melee and t2 in melee and random.randint(1, 10) <= 7:
                    continue
                break
            
            gen_ret (t1, t2, culture)

    ret_out.close()
    bld_out.write ("}\n")
    bld_out.close()
    loc_out.close()

except Exception as ex:
    print("Error:")
    traceback.print_exc(file=sys.stdout)
    input("An error has occurred. Please screenshot this error and send it to the author. Press enter to continue...")
