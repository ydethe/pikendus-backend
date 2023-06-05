      integer*4 function for_product(a, b, c)
         integer*4, intent(in) :: a, b
         integer*4, intent(out) :: c

         c = a * b

         for_product = 0

      end function
