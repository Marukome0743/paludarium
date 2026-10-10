"""U11 fixture metadata; inode identity is normalized by first path."""
import hashlib
import pathlib
import stat


def snapshot_metadata(directory):
    directory = pathlib.Path(directory)
    result, identities = {}, {}
    for path in [directory, *sorted(directory.rglob('*'))]:
        relative = str(path.relative_to(directory))
        info = path.lstat()
        kind = stat.S_IFMT(info.st_mode)
        row = {'mode': stat.S_IMODE(info.st_mode)}
        if kind == stat.S_IFDIR:
            row['kind'] = 'directory'
        elif kind == stat.S_IFLNK:
            row.update(kind='symlink', target=str(path.readlink()))
        elif kind == stat.S_IFREG:
            identity = (info.st_dev, info.st_ino)
            row.update(kind='file', sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                       identity=identities.setdefault(identity, relative), links=info.st_nlink)
        else:
            raise ValueError('unsupported native fixture object: ' + relative)
        result[relative] = row
    return result
