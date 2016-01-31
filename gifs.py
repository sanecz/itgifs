from collections import defaultdict, OrderedDict
import nltk
import it_config
import random
import tempfile
import json
import shutil

class ItGifs(object):
    def __init__(self):
        images = self.load_dict(it_config.IMAGES_DB)
        tags = self.load_dict(it_config.TAGS_DB)
        self.images = OrderedDict(sorted(images.items(), key=lambda t: t[0]))
        self.tags = OrderedDict(sorted(tags.items(), key=lambda t: t[0]))
        # it shoud look like
        # ~/nltk_data/taggers/maxent_treebank_pos_tagger/english.pickle
        self.tagger = nltk.data.load(it_config.PICKLE_FILE)

    def close(self):
        self.save_dict(self.images, it_config.IMAGES_DB)
        self.save_dict(self.tags, it_config.TAGS_DB)

    @staticmethod
    def save_dict(content, config_file):
        (fd, filename) = tempfile.mkstemp()
        with open(filename, "w") as f:
            json.dump(content, f)
        shutil.copyfile(filename, it_config.DB_PATH + config_file)

    @staticmethod
    def load_dict(config_file):
        try:
            f = open(it_config.DB_PATH + config_file, "r")
        except IOError:
            return {}
        try:
            content = json.loads(f.read())
        except ValueError:
            return {}
        f.close()
        return content

    def get_tags(self, inc_tags):
        """
        >>> t = ItGifs.__new__(ItGifs); t.tagger = nltk.data.load(it_config.PICKLE_FILE)
        >>> t.get_tags("Hello I am a unicorn")
        ['hello', 'am', 'unicorn']
        >>> t.get_tags("To in the middle and or why home")
        ['middle', 'home']
        """
        exclude = ['DT', 'TO', 'PRP', 'WRB', 'PRP$', 'TO', 'IN', 'CC']
        text = inc_tags.lower().split()
        tags = self.tagger.tag(text)
        return [elem[0] for elem in tags if elem[1] not in exclude]

    def get_image(self, inc_tags):
        """
        >>> t = ItGifs.__new__(ItGifs); t.tagger = nltk.data.load(it_config.PICKLE_FILE)
        >>> t.images = {1: ['testurl1', 'testurl2']}; t.tags = {1: ['tag1', 'tag2']}
        >>> t.get_image("nonexisting tag")
        >>> t.get_image("tag1 tag2")
        {1: ['testurl1', 'testurl2']}
        """
        found_tags = defaultdict(int)
        inc_tags = self.get_tags(inc_tags)
        for tag_id, tag in self.tags.iteritems():
            for inc_tag in inc_tags:
                if inc_tag in tag:
                    found_tags[tag_id] += 1
        found_tags = sorted(found_tags.items(), key=lambda x: x[1], reverse=True)
        if not found_tags:
            return None
        highest_value = found_tags[0][1]
        max_index = 1
        for val in found_tags:
            if val < highest_value:
                break
            max_index += 1
        item = random.choice(found_tags[0:max_index])[0]
        return {item: self.images[item]}

    def get_image_with_url(self, url):
        """
        >>> t = ItGifs.__new__(ItGifs); t.images = {1: ['testurl1', 'testurl2']}
        >>> t.get_image_with_url("testurl1")
        {1: ['testurl1', 'testurl2']}
        >>> t.get_image_with_url("testurl2")
        {1: ['testurl1', 'testurl2']}
        >>> t.get_image_with_url("pouet")
        """
        for index, image in self.images.iteritems():
            if image[0] == url or image[1] == url:
                return {index: self.images[index]}

    def get_image_with_id(self, imgid):
        """
        >>> t = ItGifs.__new__(ItGifs); t.images = {1: ['testurl1', 'testurl2']}
        >>> t.get_image_with_id(1)
        {1: ['testurl1', 'testurl2']}
        >>> t.get_image_with_id(9999)
        {9999: None}
        """
        return {imgid: self.images.get(imgid)}

    def add_image(self, url, source, inc_tags):
        """
        >>> t = ItGifs.__new__(ItGifs); t.tagger = nltk.data.load(it_config.PICKLE_FILE)
        >>> t.images = OrderedDict(); t.tags = OrderedDict()
        >>> t.add_image("testurl", "testsource", "tag1 tag2")
        True
        >>> t.add_image("testurl", "testnewsource", "tag1 tag2")
        False
        >>> t.add_image("testnewurl", "testsource", "tag1 tag2")
        False
        >>> t.images[1] == ["testurl", "testsource"] and t.tags[1] == ["tag1", "tag2"]
        True
        """
        inc_tags = self.get_tags(inc_tags)
        tagid = int(next(reversed(self.tags), 0)) + 1
        if self.get_image_with_url(url) or self.get_image_with_url(source):
            return False
        imgid = int(next(reversed(self.images), 0)) + 1
        self.images.update({imgid: [url, source]})
        self.tags.update({tagid: inc_tags})
        return True

    def del_image(self, imgid):
        """
        >>> t = ItGifs.__new__(ItGifs); t.images = {1: ["test"]}; t.tags = {1: ["test2"]}
        >>> t.del_image(1)
        >>> t.images == {} and t.tags == {}
        True
        >>> t.del_image(1) # Trying to delete a non-existing image

        """
        self.images.pop(imgid, None)
        self.tags.pop(imgid, None)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
