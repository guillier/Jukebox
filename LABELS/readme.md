
# Usage

```./jukebox.py [first label position]```

The label positions are counted from the bottom-left-hand side of the page.
If it seems a bit counter intuitive at first, there are 2 good reasons for this:

* The PDF coordinate system is working that way, so there is no need to swap values in the code
* When printing with an inkjet printer, it is better if the feeding of the page is starting with the thickest part (i.e. with labels still present on sheet). By printing, thus removing, labels always at the bottom, it is safer when doing it by small batches.


Once a label is printed, the database file ```db.yaml``` needs to be updated with ```print: no``` in the corresponding entry.


# Database format

The 'database' file ```db.yaml``` is in [http://yaml.org/](YAML) and the fields are :

* For the music labels
    * title1 [mandatory, Title of the piece]
    * title2 [optional, usually Album or Composer]
    * image [mandatory, filename]
    * category [mandatory (music1, music2, music3)]
    * duration [optional]
    * print [optional, "yes" by default]
* For the word/picture labels
    * name [mandatory, Name in one language]
    * nom [mandatory, Name in another language]
    * image [mandatory, filename]
    * category [mandatory (instrument)]
    * print [optional, "yes" by default]


# Image dimensions

Images are automatically resized and stretched but for best results, the following size are recommended:

* For the music labels : 780 x 342 pixels
* For the word/picture labels : 552 x 638 pixels


# Sources of materials

## Font

* [https://www.fontsquirrel.com/fonts/gloria-hallelujah](https://www.fontsquirrel.com/fonts/gloria-hallelujah)

Copyright (c) 2010, Kimberly Geswein ([kimberlygeswein.com](http://www.kimberlygeswein.com/))

This Font Software is licensed under the SIL Open Font License, Version 1.1.


## Sample images

(CC0 License)

* [https://www.pexels.com](https://www.pexels.com)

## Icons

(Creative Commons Attribution-NoDerivs 3.0)

* [https://www.iconsdb.com/red-icons/speaker-icon.html](https://www.iconsdb.com/red-icons/speaker-icon.html) (Red Speaker)
* [https://www.iconsdb.com/red-icons/saxophone-icon.html](https://www.iconsdb.com/red-icons/saxophone-icon.html) (Red Saxophone)

