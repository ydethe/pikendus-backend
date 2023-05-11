      integer*4 function for_area(rectptr, area)
         include 'pikendus_types.finc'

         integer*8 :: rectptr
         integer*4, intent(out) :: area

         type(rectangle) :: rect
         pointer(rectptr, rect)
         integer*4 :: tmp

         write(6,*) "[DEBUG]Ceci est un message de debug"

         tmp = (rect%ur_corner%x - rect%ll_corner%x) *
     &         (rect%ur_corner%y - rect%ll_corner%y)

         area = abs(tmp)

         for_area = 0

      end function
