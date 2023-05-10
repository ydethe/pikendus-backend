!   gfortran -g -Wpadded -Wpacked -Waliasing -Wampersand -Wsurprising -Wintrinsics-std -Wintrinsic-shadow -Wline-truncation -Wreal-q-constant -Wunused -Wunderflow -Warray-temporaries -c calcul.f -ffixed-line-length-132 -fcray-pointer -Os -fd-lines-as-comments -mavx -funroll-loops -fexpensive-optimizations -fno-range-check -fbackslash -o calcul.f.o -fPIC
      integer*4 function for_func(i, subptr)
         include 'item.finc'

         integer*8, intent (in) :: i ! input
         integer*8 :: subptr
         type(item) :: subpte
         pointer(subptr,subpte)

         integer*8 :: j

         write(6,*) "[DEBUG]Ceci est un message de debug"

         j = i**2 + i**3
         subpte%i1 = j

         for_func = 0

      end function

