'''
Created on Jun 4, 2015

@author: Connor
'''

if __name__ == '__main__':
    pass

import pkgutil, re, traceback

import client.stt as stt
import client.tts as tts
import client.modules.active as active_mods

from inspect import isclass

# Set these to False while debugging
USE_STT = False
USE_TTS = False
if not USE_TTS:
    tts.disable_tts()

def find_mods():
    """ Find modules """
    global modules
    modules = []
    print('~ Looking for modules in: '+str(active_mods.__path__).replace('\\\\', '\\')[1:-1])
    for finder, name, _ in pkgutil.iter_modules(active_mods.__path__):
        try:
            mod = finder.find_module(name).load_module(name)
            for member in dir(mod):
                obj = getattr(mod, member)
                if isclass(obj):
                    for parent in obj.__bases__:
                        if 'Module' is parent.__name__:
                            modules.append(obj())
        except Exception as e:
            print('\n~ Error loading \''+name+'\' '+str(e))        
    modules.sort(key=lambda mod: mod.priority, reverse=True)

def list_mods():
    """ List module order """
    print('\n~ Module Order: ', end='')
    print(str([mod.name for mod in modules])[1:-1]+'\n')

def greet():
    """ Greet the user """
    print('     _   _   _                      ')
    print('    / \ | |_| |__   ___ _ __   __ _ ')
    print('   / _ \| __| \'_ \ / _ \ \'_ \ / _` |')
    print('  / ___ \ |_| | | |  __/ | | | (_| |')
    print(' /_/   \_\__|_| |_|\___|_| |_|\__,_|')
    print('      __     __    _                ')
    print('      \ \   / /__ (_) ___ ___       ')
    print('       \ \ / / _ \| |/ __/ _ \      ')
    print('        \ V / (_) | | (_|  __/      ')
    print('         \_/ \___/|_|\___\___|      ')
    print('\n~ Hello, what can I do for you today?\n')

def execute_tasks(mod, text):
    """ Executes a module's task queue """
    for task in mod.task_queue:
        task.action(text)
        if task.greedy:
            break

def build_mod_order(mods):
    """ Executes a module's task queue """
    mods.sort(key=lambda mod: mod.priority, reverse=True)
    normal_mods = []
    greedy_flag = False
    greedy_mods = []
    priority = 0
    for mod in mods:
        if greedy_flag and mod.priority < priority:
            break
        if mod.greedy:
            greedy_mods.append(mod)
            greedy_flag = True
            priority = mod.priority
        else:
            normal_mods.append(mod)
            
    greedy_mod = greedy_mods[0]
    if 1 < len(greedy_mods):
        if 0 < len(normal_mods):
            print("\n~ Matched mods (non-greedy): "+str([mod.name for mod in normal_mods])[1:-1]+'\n')
        greedy_mod = mod_select(greedy_mods)
    normal_mods.append(greedy_mod)
    return normal_mods
    
def execute_mods(mods, text):
    for mod in mods:
        execute_tasks(mod, text)
        
def mod_select(mods):
    """ Prompt user to specify which module to use to respond """
    print('\n~ Which module (greedy) would you like me to use to respond?')
    print('~ Choices: '+str([mod.name for mod in mods])[1:-1]+'\n')
    mod_select = input('> ')
    
    for mod in mods:
        if re.search('^.*\\b'+mod.name+'\\b.*$',  mod_select, re.IGNORECASE):
            return mod
    print('\n~ No module name found.\n')

def match_mods(text):
    global modules
    matched_mods = []
    for mod in modules:
        """ Find matched tasks and add to module's task queue """
        mod.task_queue = []
        for task in mod.tasks:
            if task.match(text):
                mod.task_queue.append(task)
                if task.greedy:
                    break
                
        """ Add modules with matched tasks to list """
        if len(mod.task_queue):
            matched_mods.append(mod)
    return matched_mods

def run():
    while True:
        try:
            if USE_STT:
                stt.listen_keyword()
                text = stt.active_listen()
            else:
                text = input('> ')
            if not text:
                print("\n~ No text input received.\n")
                continue
    
            matched_mods = match_mods(text)
                     
            if len(matched_mods) == 0:
                print('\n~ No modules matched.\n')
            else:
                mods = build_mod_order(matched_mods)
                execute_mods(mods, text)
                
        except EOFError:
            print('\n\n~ Shutting down.\n')
            break
        except:
            print(traceback.format_exc())
            tts.speak("Error occurred. Would you still like to continue?")
            print("Error occurred. Would you still like to continue?\n")
            response = input('> ')
            #response = stt.active_listen()
            
            if "yes" not in response.lower():
                break
    print('~ Arrivederci.')

find_mods()
list_mods()
greet()
stt.init()
run()
