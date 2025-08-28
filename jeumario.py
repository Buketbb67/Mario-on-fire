import pygame
from pygame import *

import random 
import os

base_path = os.path.expanduser("~")  # récupère le chemin C:\Users\buket pour ensuite récupérer les images 

def get_image_path(*path_parts): # fonction pour récupérer le chemin d'accès avec toutes les images 
    return os.path.join(base_path, "Desktop", "Epitech", "Projet jeu vidéo type Mario Bros", *path_parts)

def get_sound_path(*path_parts): # fonction pour récupérer le chemin d'accès aux sons 
    return os.path.join(base_path, "Desktop", "Epitech", "Projet jeu vidéo type Mario Bros", "sons", *path_parts)

#pour récuperer pygame 
pygame.init()

#pour donner un titre à notre écran 
pygame.display.set_caption("Mario on fire")

# Définir les dimensions de l'écran
LARGEUR_ECRAN = 800
HAUTEUR_ECRAN = 600

#création de l'écran avec sa taille et option resizable qui permet de changer la taille de la page sans changer la taille des composants 
ecran = pygame.display.set_mode([LARGEUR_ECRAN, HAUTEUR_ECRAN], RESIZABLE)  

# fonction pour tout redimensionner en fonction de la taille de la page 
def redimensionner():
    global banniere_redim, play_button_redim, play_button_rect, game_over_redim
    banniere_redim = pygame.transform.scale(banniere, (LARGEUR_ECRAN, int(HAUTEUR_ECRAN * 0.8)))
    play_button_redim = pygame.transform.scale(play_button, (int(LARGEUR_ECRAN * 0.5), int(HAUTEUR_ECRAN * 0.5)))
    play_button_rect = play_button_redim.get_rect(center=(LARGEUR_ECRAN // 2, HAUTEUR_ECRAN // 2))
    game_over_redim = pygame.transform.scale(game_over,(LARGEUR_ECRAN, HAUTEUR_ECRAN))
    
#création image arrière plan
background = pygame.image.load(get_image_path("decor_mario_bros.png")).convert()

# création de la bannière 
banniere = pygame.image.load(get_image_path("banniere.png")).convert()
banniere.set_colorkey((255, 255, 255)) # cela sert à rendre le fond de la bannière qui était blanc, transparent 

# creation du boutton play 
play_button = pygame.image.load(get_image_path("bouton_play.png")).convert()
play_button.set_colorkey((255, 255, 255))
play_button_rect = play_button.get_rect() # permet de récupérer la position du boutton jouer 

# création image game over 
game_over = pygame.image.load(get_image_path("game_over_mario.png")).convert_alpha()

redimensionner()
# on va créer une classe pour le fait de jouer 
class Jouer(pygame.sprite.Sprite): 
    def __init__(self):
        # pour définir si le jeu est lancé par le joueur ou non (on part sur false et quand le joueur clique sur jouer on passe en true)
        self.is_playing = False 
        # la classe Son devient son 
        self.son = Son()

    def reset(self):
        global mario, tous_sprites, les_ennemis

        # Réinitialiser Mario
        mario = Mario()
        mario.repositionner()
        # Vider les groupes de sprites
        tous_sprites.empty()
        les_ennemis.empty()

        # Réajouter Mario dans les groupes
        tous_sprites.add(mario)

        # Démarrer la partie
        self.is_playing = True

    def update(self,dt) :
         
         # Dessiner tous les sprites
        global ecran # ici on met global pour que le terminal ne pense pas que j'essaye de créer une nouvelle variable ecran mais que j'utilise bien celle qui existe deja
        nouveau_background = pygame.transform.scale(background, (LARGEUR_ECRAN, HAUTEUR_ECRAN))
        ecran.blit(nouveau_background, (0, 0))

        for mon_sprite in tous_sprites:
            ecran.blit(mon_sprite.surface, mon_sprite.rect)
    
        # pour la maj de la barre de vie de Mario 
        if mario.alive():
            mario.update_health_bar(ecran)

 # pour les dégats que mario se prend quand un ennemi le touche 
        for ennemi in les_ennemis:
            if mario.alive() and mario.rect.colliderect(ennemi.rect):
                mario.damage(50) 
                jeu.son.play('blessure')
                les_ennemis.remove(ennemi)
                tous_sprites.remove(ennemi)   
            break  # éviter plusieurs collisions en même temps
    
    # mettre à jour les entrées utilisateur pour mario 
        if mario.alive():
            touche_appuyee = pygame.key.get_pressed()
            mario.update(touche_appuyee, dt)
            mario.tous_projectilesfeu.update()
            mario.update_health_bar(ecran)
    
        if mario.health == 0 : 
            mario.kill()
            ecran.fill((0, 0, 0))  # Fond noir
            ecran.blit(game_over_redim, (0,0))
            pygame.time.wait(1000)
            pygame.mixer.music.stop()
            jeu.son.play('mort')
            pygame.display.flip()
            pygame.time.wait(4000)
            # permet de retourner au menu d'accueil 
            self.is_playing = False

    # Mettre à jour les entrées utilisateur  
        les_ennemis.update()
    # détecter les collisions entre les projectiles et les ennemis (cela va tuer l'ennemi et faire disparaitre le projectile)
        if pygame.sprite.groupcollide(mario.tous_projectilesfeu, les_ennemis, True, True):
            print("Un ennemi a été touché !")

def get_hauteur_sol():
    return HAUTEUR_ECRAN - 90

# une classe qui permet de gérer les effets sonores 
class Son(pygame.sprite.Sprite):
    def __init__(self) : 
        # on crée un dictionnaire pour enregistrer les différents bruitages 
        self.sounds = {
            'feu':pygame.mixer.Sound(get_sound_path("fireball.ogg")) , 
            'mort': pygame.mixer.Sound(get_sound_path("mort.ogg")),
            'blessure': pygame.mixer.Sound(get_sound_path("pvmoins.ogg")) 
        }
        #self.sounds_volume = pygame.mixer.Sound.set_volume(0.10)
        self.music = pygame.mixer_music.load(get_sound_path("overworld.ogg"))
        self.music_volume = pygame.mixer.music.set_volume(0.25)
        self.music_play = pygame.mixer.music.play(loops=-1) # le -1 permet de repeter la musique a l'infini
        
        self.sound_volume()

    def play(self, name):
        self.sounds[name].play()
    
    def sound_volume(self) : 
        for sound in self.sounds.values():
            sound.set_volume(0.10)        

#on va créer un objet qui sera le héro du jeu 
class Mario(pygame.sprite.Sprite):
    def __init__(self): #c'est la fonction qui permet de dire comment on crée notre objet 
        super().__init__() #c'est quoi super ?               
        image_origine = pygame.image.load(get_image_path("firemario.jpg")).convert()
        image_redimensionnee = pygame.transform.scale(image_origine, (100, 120))  # largeur, hauteur 
        image_redimensionnee.set_colorkey((255, 255, 255), RLEACCEL) # RLEACCEL permet de rendre le fond de l'image transparent 
        self.surface = image_redimensionnee
        self.rect = self.surface.get_rect( #on définit la position de mario  
            center =( 
            LARGEUR_ECRAN -700,   
            HAUTEUR_ECRAN -150,
            )
        )
        self.health = 100
        self.max_health = 100 
        self.attack = 10
        self.velocity = 5 # vitesse à laquelle se déplace le personnage 
        self.is_jumping = False # on définit le boléen pour faire sauter mario 
        self.velocity_y = 0
        self.gravity = 1500  # pixels/sec²
        self.jump_velocity = -600  # vers le haut
        self.ground_y = self.rect.bottom  # position du sol initiale
        self.tous_projectilesfeu = pygame.sprite.Group() # chauque projectile lancé par le joueur sera rangé dans le groupe sprite  
        self.touches = 0 
        self.est_au_sol = True
        self.nb_sauts = 0
        self.saut_max = 3

# pour repositionner mario quand on agrandi l'écran 
    def repositionner(self):
        # Exemple : Mario reste en bas à gauche, avec un petit décalage
        self.rect.bottomleft = (20, HAUTEUR_ECRAN - 80)
        if mario.est_au_sol:
            mario.rect.bottom = get_hauteur_sol()

# pour gérer les dégats que se prend mario 
    def damage(self, amount):
        self.touches += 1
        self.health -= amount

        if self.touches >= 2:
            self.kill()

# pour la gestion des pv de mario (il a deux vies)
    def update_health_bar(self, surface):
        bar_couleur = (111,210,46) # la jauge de vie en vert 
        back_bar_couleur = (60,63,60) # arrière plan de la jauge en gris 
        bar_position = [self.rect.centerx -45, self.rect.centery - 85, self.health,10] # propriété de la barre de vie 
        back_bar_position = [self.rect.centerx -45, self.rect.centery - 85, self.max_health,10] # propriété de la barre en fonction des pv max
        
        pygame.draw.rect(surface, back_bar_couleur, back_bar_position) # afficher la bar de vie
        pygame.draw.rect(surface, bar_couleur, bar_position) # afficher la vie restant 
        
# y(t) = -0.5 * g * t**2 + v0 * t + y0 == fonction parabolique à utiliser pour faire sauter le personnage 
# on prend en compte la position de départ avec la vitesse de déplacement par rapport à la gravité 
   
# fonction qui définit ce qu'il se passe quand le joueur appuie sur une touche 
    def update(self, pressed_keys, dt):    
        if pressed_keys[K_DOWN] : 
            self.rect.move_ip(0,5)
        if pressed_keys[K_RIGHT] : 
            self.rect.move_ip(self.velocity,0)
        if pressed_keys[K_LEFT] : 
            self.rect.move_ip(- self.velocity,0)
        
   # detecter la gravité du saut  
        if self.is_jumping:
            self.velocity_y += self.gravity * dt
            self.rect.bottom += self.velocity_y * dt
    # detecter le sol 
        if self.rect.bottom >= get_hauteur_sol():
            self.rect.bottom = get_hauteur_sol()
            self.is_jumping = False
            self.velocity_y = 0
            self.est_au_sol = True
            self.nb_sauts = 0  # reset des sauts
        else:
            self.est_au_sol = False
            
        # pour que mario ne puis pas sortir de l'écran 
        if self.rect.left < 0 : 
            self.rect.left = 0 
        if self.rect.right > LARGEUR_ECRAN:
            self.rect.right = LARGEUR_ECRAN
        if self.rect.top <= 0: 
            self.rect.top = 0
        if self.rect.bottom >= HAUTEUR_ECRAN : 
            self.rect.bottom = HAUTEUR_ECRAN 
            
    def lancer_feu(self):
        feu = Projectile_feu(self.rect.right +40, self.rect.top +40) # je rajoute entre parenthèse la position du projectile par rapport à Mario 
        self.tous_projectilesfeu.add(feu) # chaque projectile lancé est ajouté au groupe des projectiles 
        tous_sprites.add(feu)

#on définit la variable mario qui est égal à la classe Mario 
mario = Mario()

class Projectile_feu (pygame.sprite.Sprite): 
    def __init__(self, x, y) : 
        super().__init__()
        self.velocity = 5
        image_path = pygame.image.load(get_image_path("boule.png")).convert() 
        image_finale = pygame.transform.scale(image_path, (50, 50))
        image_finale.set_colorkey((255, 255, 255), RLEACCEL)
        self.surface = image_finale
        self.rect = self.surface.get_rect(center=(x,y))
        self.speed = 10

    def update(self):# on utilise update car c'est ce que va appeler automatiquement 
        self.rect.move_ip(self.speed, 0)
        if self.rect.right > LARGEUR_ECRAN : 
            self.kill()

class Ennemi(pygame.sprite.Sprite): 
    def __init__(self) :
        super(Ennemi, self).__init__()
        self.surface = pygame.image.load(get_image_path("champi1.png")).convert()
        self.surface.set_colorkey((255,255,255), RLEACCEL) #on rempli en blanc notre objet 
        # apparition des ennemis à droite de l'écran 
        self.rect = self.surface.get_rect (
            center =( 
            LARGEUR_ECRAN + 2,
            HAUTEUR_ECRAN -135,
            )
        )
        self.speed = random.randint(5, 20) #vitesse prise au hasard entre 5 et 20

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0 : 
            self.kill()
   
#création de la variable horloge pour ralentir le jeu 
clock = pygame.time.Clock()

#pour afficher tous les objets en même temps, on les regroupe, les sprites c'est ce qu'on voit à l'écran 
tous_sprites = pygame.sprite.Group()
#on ajoute Mario dans les sprites 
tous_sprites.add(mario)

#on crée un groupe pour les ennemis 
les_ennemis = pygame.sprite.Group()

#on cree un evenement pour ajouter des ennemis 
AJOUT_ENNEMI = pygame.USEREVENT +1
pygame.time.set_timer(AJOUT_ENNEMI, 1500) # on ajoute un ennemi toutes les x millisecondes 

#création de la boucle principale 
continuer = True 
nb_touches = 0
jeu = Jouer()

while continuer : 
    # Ralentir la boucle ici on met en secondes  
    dt = clock.tick(60)/1000

    # GÉRER LES ÉVÉNEMENTS 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
                continuer = False
                pygame.quit()
        elif event.type == pygame.KEYDOWN :
            if not jeu.is_playing :
                jeu.is_playing = True
            elif jeu.is_playing:
                if event.key == pygame.K_z: # pour lancer une seule boule de feu à la fois car sinon ça en lance 60 par sec (cf 60 FPS)
                    mario.lancer_feu()
                    jeu.son.play('feu')
                if event.key == pygame.K_SPACE and mario.nb_sauts < mario.saut_max:
                    mario.is_jumping = True
                    mario.velocity_y = mario.jump_velocity
                    mario.nb_sauts += 1
                    mario.est_au_sol = False
            # on redimensionne 
        elif event.type == VIDEORESIZE:
                LARGEUR_ECRAN, HAUTEUR_ECRAN = event.size
                ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN), RESIZABLE)
                redimensionner()
                mario.repositionner()
                # pour repositionner correctement mario 
                if mario.est_au_sol:
                    mario.rect.bottom = get_hauteur_sol()
            # on ajoute des ennemis 
        elif event.type == AJOUT_ENNEMI and jeu.is_playing:
                nouvel_ennemi = Ennemi()
                les_ennemis.add(nouvel_ennemi)
                tous_sprites.add(nouvel_ennemi)
        elif event.type == pygame.MOUSEBUTTONDOWN : 
                # verifier si la souris touche le boutton jouer 
            if not jeu.is_playing and play_button_rect.collidepoint(event.pos): # cela permet de bloquer les actions avec la souris pdt la partie 
                    jeu.reset()

    if jeu.is_playing :
        # déclencher les instructions de la partie 
        jeu.update(dt)
    # verifier si le jeu n'a pas commencé et ajouter l'ecran de bienvenue 
    else:
    # Redimensionner le fond selon la taille actuelle de l'écran
        nouveau_background = pygame.transform.scale(background, (LARGEUR_ECRAN, HAUTEUR_ECRAN))
        ecran.blit(nouveau_background, (0, 0))  # D'abord le fond
    # Afficher la bannière par-dessus
        ecran.blit(banniere_redim, (0, 0))
        ecran.blit(play_button_redim, play_button_rect)
    # Affichage final
    pygame.display.flip()
