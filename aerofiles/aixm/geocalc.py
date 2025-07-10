import decimal
import math

# Converter function to convert nautical miles to km
#
# @param nm nautical miles
#
# @return corresponding value in km


def nautical_miles_to_km(nm):
    return nm * decimal.Decimal(1.852)


def geo_destination(p, angle, distance_km: float):
    lat1 = p.latitude
    lon1 = p.longitude

    angle = math.radians(angle)
    dx = math.sin(angle) * distance_km
    dy = math.cos(angle) * distance_km

    (kx, ky) = get_kx_ky(lat1)

    lon2 = lon1 + dx / kx
    lat2 = lat1 + dy / ky

    return (lat2, lon2)


# Compute the distance between two GPS points in 2 dimensions
# (without altitude). Latitude and longitude parameters must be given
# as fixed integers multiplied with GPS_COORD_MULT.
#
# \param lat1 the latitude of the 1st GPS point
# \param lon1 the longitude of the 1st GPS point
# \param lat2 the latitude of the 2nd GPS point
# \param lon2 the longitude of the 2nd GPS point
# \param FAI use FAI sphere instead of WGS ellipsoid
# \param bearing pointer to bearing (NULL if not used)
#
# \return the distance in cm.
#
def geo_distance(p1, p2):

    lat1 = p1.latitude
    lon1 = p1.longitude
    lat2 = p2.latitude
    lon2 = p2.longitude

    d_lon = (lon2 - lon1)
    d_lat = (lat2 - lat1)

    # DEBUG("#d_lon=%0.10f\n", d_lon);
    # DEBUG("#d_lat=%0.10f\n", d_lat);

    # DEBUG("lat1=%li\n", lat1);
    # DEBUG("lon1=%li\n", lon1);
    # DEBUG("lat2=%li\n", lat2);
    # DEBUG("lon2=%li\n", lon2);

    # WGS
    # DEBUG("f=0\n");
    # DEBUG("#lat=%0.10f\n", (lat1 + lat2) / ((float)GPS_COORD_MUL * 2));

    (kx, ky) = get_kx_ky((lat1 + lat2) / 2)

    # DEBUG("#kx=%0.10f\n", kx);
    # DEBUG("#ky=%0.10f\n", ky);

    d_lon = d_lon * kx
    d_lat = d_lat * ky

    # DEBUG("#d_lon=%0.10f\n", d_lon);
    # DEBUG("#d_lat=%0.10f\n", d_lat);

    dist = math.sqrt(math.pow(d_lon, 2) + math.pow(d_lat, 2)) * 100000.0

    if d_lon == 0 and d_lat == 0:
        bearing = 0
    else:
        bearing = (math.degrees(math.atan2(d_lon, d_lat)) + 360) % 360
        # DEBUG("a=%d\n", *bearing);

    # DEBUG("d=%lu\n\n", dist);

    return (dist, bearing)


def get_kx_ky(lat):
    fcos = math.cos(math.radians(lat))
    cos2 = 2. * fcos * fcos - 1.
    cos3 = 2. * fcos * cos2 - fcos
    cos4 = 2. * fcos * cos3 - cos2
    cos5 = 2. * fcos * cos4 - cos3
    # multipliers for converting longitude and latitude
    # degrees into distance (http://1.usa.gov/1Wb1bv7)
    kx = (111.41513 * fcos - 0.09455 * cos3 + 0.00012 * cos5)
    ky = (111.13209 - 0.56605 * cos2 + 0.0012 * cos4)
    return (kx, ky)


def decimal_degrees_to_dms(decimal_degrees):
    # mnt,sec = divmod(decimal_degrees*3600,60)
    # deg,mnt = divmod(mnt, 60)
    # return (round(deg),round(mnt),round(sec))

    # decimals, number = math.modf(decimal_degrees)
    # deg = int(number)
    # mnt = round(decimals * 60)
    # sec = (decimal_degrees - deg - mnt / 60) * 3600.00
    # return deg,mnt,round(sec)

    decimals, number = math.modf(decimal_degrees)
    deg = int(number)
    mnt = int(decimals * 60)
    sec = round((decimal_degrees - deg - mnt / 60) * 3600.00)
    if sec == 60:
        sec = 0
        mnt += 1
        if mnt == 60:
            mnt = 0
            deg += 1
    return deg, mnt, sec


def strDegree(v, width):
    (degrees, minutes, seconds) = decimal_degrees_to_dms(abs(v))
    return f'{degrees:0{width}d}:{minutes:02d}:{seconds:02d}'


def strLatLon(P):
    result = strDegree(abs(P[0]), 2) + " "
    if P[0] >= 0:
        result = result + "N "
    else:
        result = result + "S "

    result = result + strDegree(abs(P[1]), 3) + " "
    if P[1] >= 0:
        result = result + "E "
    else:
        result = result + "W "
    return result
