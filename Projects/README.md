Ce dossier contient les différents projet réalisé. 
Chaque dossier et repertorié de la manière suivante: 
   <n°prjt>-<plateforme_de_création>-<nb_images_dataset>i-<type_img>

n°prjt: numéro du projet

plateforme_de_création: plateforme ou le projet a été crée
   ex: EI -> EdgeImpluse

nb_images_dataset: nombre d'images utilisé dans le dataset 
   ex : 100i -> 100 images

type_img : type d'image utilisé
   ex :  pv -> peu de voiture sur l'image
         bv -> beaucoup de voiture
         <type_img>+"c" -> image avec des voitures cachées (coupée) ou peu visible 

Organisation de chaque projet: 
<n°prjt>-<plateforme_de_création>-<nb_images_dataset>i-<type_img>:
- inoFiles :
   |- CAM :
      |- fichier main modifié pour le CAM
   |- EYE : 
      |- fichier main modifié pour le EYE
   |- SENSE : 
      |- fichier main modifié pour le SENSE
- LIB-<n°prjt>-<plateforme_de_création>-<nb_images_dataset>i-<type_img>: #lib pour le projet exporté via la plateform
- info.txt #info sur le projet