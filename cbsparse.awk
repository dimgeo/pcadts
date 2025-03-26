BEGIN {
        FS=";"
        OFS=","
}
FNR <=3{
        next;
}
{
        gsub("Leeftijdsopbouw Nederland ","", FILENAME);
        gsub(".csv","", FILENAME);
        gsub(" jaar","",$1);
        gsub (" ","", $2);
        gsub (" ","",$3) ;
        print FILENAME,$1, $2 , $3 ;
}

