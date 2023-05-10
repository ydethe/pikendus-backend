#include <stdint.h>
#include <math.h>
#include "_pikendus_types.h"


int c_create_rectangle(rectangle *r, uint32_t width, uint32_t height)
{
    r->ll_corner.x=0;
    r->ll_corner.y=0;

    r->ur_corner.x=width;
    r->ur_corner.y=height;

    return 0;

}
