      integer*4 function for_area(rectptr, area)
         include 'pikendus_types.finc'

         integer*8 :: rectptr
         integer*4, intent(out) :: area

         type(rectangle) :: rect
         pointer(rectptr, rect)

         write(6,*) "[DEBUG]Ceci est un message de debug"

         area = (rect%ur_corner%x - rect%ll_corner%x) *
     &          (rect%ur_corner%y - rect%ll_corner%y)

         area = abs(area)

         for_area = 0

      end function

