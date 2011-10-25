import math
import os

methods = {}
for i in xrange(20):
    methods[ i ] = 0

def bytesToInt(f, f_pos, ln):
    prev_pos = f.tell()
    f.seek(f_pos)
    tmp = 0
    for i in xrange(ln):
        f.seek(f_pos + ln-1 - i)
        tmp = tmp * 256 + ord(f.read(1))
    f.seek(prev_pos)
    return tmp

def intToByteString(num):
    if num == 0:
        return '0x0'
    bs = ''
    #while num > 0:
    for i in xrange(8):
        b = num % 16
        bc = ''
        if b > 9:
            bc = chr(b-10 + ord('a'))
        else:
            bc = chr(b + ord('0'))
        bs = bc + bs
        num = num / 16
    bs = '0x' + bs
    return bs


class EndOfCentralDirectoryRecord:
    '''
        end of central dir signature    4 bytes  (0x06054b50)
        number of this disk             2 bytes
        number of the disk with the
        start of the central directory  2 bytes
        total number of entries in the
        central directory on this disk  2 bytes
        total number of entries in
        the central directory           2 bytes
        size of the central directory   4 bytes
        offset of start of central
        directory with respect to
        the starting disk number        4 bytes
        .ZIP file comment length        2 bytes
        .ZIP file comment       (variable size)
    '''
    def __init__(self, f, f_pos):
        prev_pos = f.tell()
        f.seek(f_pos)

        self.sig = bytesToInt(f, f_pos+0, 4)
        self.n_disk = bytesToInt(f, f_pos+4, 2)
        self.n_disk_w_st = bytesToInt(f, f_pos+6, 2)
        self.tn_entry_on_disk = bytesToInt(f, f_pos+8, 2)
        self.tn_entry_in_c_dir = bytesToInt(f, f_pos+10, 2)
        self.size = bytesToInt(f, f_pos+12, 4)
        self.off_c_dir_w_disk_num = bytesToInt(f, f_pos+16, 4)

        f.seek(prev_pos)

        print ' '
        print 'end of central dir signature:', self.sig
        print ' '
        print 'number of this disk:', self.n_disk
        print ' '
        print 'number of the disk with the'
        print 'start of the central directory:', self.n_disk_w_st
        print ' '
        print 'total number of entries in the'
        print 'central directory on this disk:', self.tn_entry_on_disk
        print ' '
        print 'total number of entries in'
        print 'the central directory:', self.tn_entry_in_c_dir
        print ' '
        print 'size of the central directory:', self.size
        print ' '
        print 'offset of start of central'
        print 'directory with respect to'
        print 'the starting disk number:', self.off_c_dir_w_disk_num
        print '   : possibly overflowed'
        print ' '


class FileHeader:
    '''
        central file header signature   4 bytes  (0x02014b50)
        version made by                 2 bytes
        version needed to extract       2 bytes
        general purpose bit flag        2 bytes
        compression method              2 bytes
        last mod file time              2 bytes
        last mod file date              2 bytes
        crc-32                          4 bytes
        compressed size                 4 bytes
        uncompressed size               4 bytes
        file name length                2 bytes
        extra field length              2 bytes
        file comment length             2 bytes
        disk number start               2 bytes
        internal file attributes        2 bytes
        external file attributes        4 bytes
        relative offset of local header 4 bytes

        file name (variable size)
        extra field (variable size)
        file comment (variable size)
    '''
    def __init__(self, f, f_pos):
        prev_pos = f.tell()
        f.seek(f_pos)

        self.sig = bytesToInt(f, f_pos+0, 4)
        self.ver_mb = bytesToInt(f, f_pos+4, 2)
        self.ver_n = bytesToInt(f, f_pos+6, 2)
        self.flag = bytesToInt(f, f_pos+8, 2)
        self.comp = bytesToInt(f, f_pos+10, 2)
        self.mod_time = bytesToInt(f, f_pos+12, 2)
        self.mod_date = bytesToInt(f, f_pos+14, 2)
        self.crc32 = bytesToInt(f, f_pos+16, 4)
        self.comp_size = bytesToInt(f, f_pos+20, 4)
        self.uncomp_size = bytesToInt(f, f_pos+24, 4)
        self.name_len = bytesToInt(f, f_pos+28, 2)
        self.extra_field_len = bytesToInt(f, f_pos+30, 2)
        self.comment_len = bytesToInt(f, f_pos+32, 2)
        self.disk_num = bytesToInt(f, f_pos+34, 2)
        self.int_file_attr = bytesToInt(f, f_pos+36, 2)
        self.ext_file_attr = bytesToInt(f, f_pos+38, 4)
        self.off_local_header = bytesToInt(f, f_pos+42, 4)

        f.seek(f_pos + 46)
        self.name = ''
        for i in xrange(self.name_len):
            self.name += f.read(1)

        self.extra_field = ''
        for i in xrange(self.extra_field_len):
            self.extra_field += f.read(1)

        self.comment = ''
        for i in xrange(self.comment_len):
            self.comment += f.read(1)

        self.len = f.tell() - f_pos

        f.seek(prev_pos)


class LocalHeader:
    '''
        local file header signature     4 bytes  (0x04034b50)
        version needed to extract       2 bytes
        general purpose bit flag        2 bytes
        compression method              2 bytes
        last mod file time              2 bytes
        last mod file date              2 bytes
        crc-32                          4 bytes
        compressed size                 4 bytes
        uncompressed size               4 bytes
        file name length                2 bytes
        extra field length              2 bytes

        file name (variable size)
        extra field (variable size)
    '''
    def __init__(self, f, f_pos):
        prev_pos = f.tell()
        f.seek(f_pos)

        self.sig = bytesToInt(f, f_pos+0, 4)
        self.ver_n = bytesToInt(f, f_pos+4, 2)
        self.flag = bytesToInt(f, f_pos+6, 2)
        self.comp = bytesToInt(f, f_pos+8, 2)
        self.mod_time = bytesToInt(f, f_pos+10, 2)
        self.mod_date = bytesToInt(f, f_pos+12, 2)
        self.crc32 = bytesToInt(f, f_pos+14, 4)
        self.comp_size = bytesToInt(f, f_pos+18, 4)
        self.uncomp_size = bytesToInt(f, f_pos+22, 4)
        self.name_len = bytesToInt(f, f_pos+26, 2)
        self.extra_field_len = bytesToInt(f, f_pos+28, 2)

        f.seek(f_pos + 30)
        self.name = ''
        for i in xrange(self.name_len):
            self.name += f.read(1)

        self.extra_field = ''
        for i in xrange(self.extra_field_len):
            self.extra_field += f.read(1)

        self.len = f.tell() - f_pos

        f.seek(prev_pos)


def findSigBackward(f, sig):
    print 'looking for sig', sig

    sig_bytes = []
    for i in xrange(4):
        sig_bytes.append(chr(sig % 256))
        sig = sig / 256

    f.seek(0, 2)
    size = f.tell()
    i = 4 + 100000 * 0
    z = 0
    while i < size:
        f.seek(-1*i, 2)
        chk = 0
        for j in xrange(4):
            if f.read(1) == sig_bytes[j]:
                chk += 1
        if chk == 4:
            f.seek(-1*i, 2)
            res = 0
            sig = 0
            for j in xrange(4):
                res = res * 256 + ord(f.read(1))
                sig = sig * 256 + ord(sig_bytes[j])
            print 'find sig at', i, ':', res, '==', sig
            return i
        i += 1
    print 'fail to find sig'

def decompressMember(f, lh, fh):
    import zlib
    decomp = zlib.decompressobj(-15)
    decomp_end = fh.off_local_header + lh.len + fh.comp_size
    min_read = 4096
    buf = ''
    unconsumed = ''
    off = 0

    n = 4096
    f.seek(fh.off_local_header + lh.len)
    chkp = f.tell()

    print 'decompressing... size:', fh.uncomp_size

    if not os.path.exists(os.path.dirname(fh.name)):
        os.makedirs(os.path.dirname(fh.name))
    out = open(fh.name, 'wb')
    while f.tell() < decomp_end or len(unconsumed) != 0:
        buf_margin = len(buf) - off
        left = decomp_end - f.tell()
        if left > 0 and n > buf_margin + len(unconsumed):
            next_read = n - buf_margin - len(unconsumed)
            next_read = max(next_read, min_read)
            next_read = min(next_read, decomp_end - f.tell())
            data = f.read(next_read)
            if fh.comp == 0:
                buf = buf[off:] + data
                off = 0
            else:
                unconsumed += data
        if len(unconsumed) > 0 and n > buf_margin and fh.comp == 8:
            data = decomp.decompress(unconsumed, max(n - buf_margin, min_read))
            unconsumed = decomp.unconsumed_tail
            if len(unconsumed) == 0 and left == 0:
                data += decomp.flush()
            buf = buf[off:] + data
            off = 0
        data = buf[off:off + n]
        off += len(data)

        if f.tell() - chkp > 1024 * 1024:
            chkp = f.tell()
            print decomp_end - f.tell(), 'left'

        out.write(data)
    out.close()
    print 'decompressing complete'

def enumArchive(f, mode):
    print 'enumerate archive', f.name

    f.seek(0, 2)
    size = f.tell()

    sig = 0x06054b50
    sig_pos = size - findSigBackward(f, sig)
    print 'sig at', sig_pos, 'size', size

    ecdr = EndOfCentralDirectoryRecord(f, sig_pos)
    # overcome overflow
    ecdr.off_c_dir_w_disk_num = sig_pos - ecdr.size
    print 'overcome overflow :', ecdr.off_c_dir_w_disk_num
    print ' '
    f_pos = ecdr.off_c_dir_w_disk_num

    header_sig = 0x02014b50

    #f_pos = 14848734575 # jump to error pos
    print 'seek every header from', f_pos
    z = 0
    n = 0
    while f_pos + 4 < size:
        chk = 0
        pos_sig = bytesToInt(f, f_pos, 4)
        if header_sig == pos_sig:
            # start of a header
            print 'header at', f_pos
            fh = FileHeader(f, f_pos)
            print fh.name

            if fh.off_local_header >= 0:
                loc_sig = 0x04034b50
                loc_pos = f_pos + fh.off_local_header
                loc_pos = 0 + fh.off_local_header
                loc_pos_sig = 0
                while loc_sig != loc_pos_sig:
                    loc_pos_sig = bytesToInt(f, loc_pos, 4)
                    if loc_sig == loc_pos_sig:
                        fh.off_local_header = loc_pos
                        lh = LocalHeader(f, fh.off_local_header)
                        '''
                        if lh.flag != 0 and lh.flag != 8:
                            print 'flag', lh.flag
                            return
                        methods[ fh.comp ] += 1
                        '''
                        if fh.comp_size and fh.uncomp_size and fh.crc32:
                            decompressMember(f, lh, fh)
                        else:
                            if not os.path.exists(fh.name):
                                os.makedirs(fh.name)
                        break
                        '''
                        print 'name\t', lh.name, fh.name
                        print 'crc32\t', lh.crc32, fh.crc32
                        print 'comp\t', lh.comp_size, fh.comp_size
                        print 'uncomp\t', lh.uncomp_size, fh.uncomp_size
                        break
                        print 'found!', loc_pos, fh.off_local_header
                        print 'diff', loc_pos - fh.off_local_header
                        print 'off', fh.off_local_header
                        return
                        '''
                    else:
                        '''
                        print 'local header sig not matching at', loc_pos
                        print 'found', intToByteString(loc_pos_sig)
                        print 'expct', intToByteString(loc_sig)
                        '''
                        loc_pos += 0x100000000
                        if loc_pos > size:
                            print 'not found'
                            return

            # f_pos += 4 + fh.len
            '''
            n += 1
            if n==3:
                return
            '''
        ''' just to make sure
        else:
            f_pos += 1
        '''
        
        f_pos += 1

        z += 1
        if z == 1000000:
            print f_pos
            z = 0
zipname = ''
print '\n\n\n'
if zipname != '':
    print 'start recovery for', zipname
else:
    print 'modify script for zipname'

f = open(zipname)
enumArchive(f, 0)
#print methods
