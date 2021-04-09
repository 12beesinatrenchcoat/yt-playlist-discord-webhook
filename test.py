# Unit tests, I guess.
import unittest
import typing
import main

# A test playlist created by myself to test various features of the script.
# It contains five videos, added by two different users,
# and some videos don't have maxres thumbnails.
# This playlist shouldn't be changed.
TEST_PLAYLIST: typing.Final = 'PLB2AcRG34VQWlArTnlLR98RZeOnep8-Zb'


# Testing functions revolving around YouTube and video filtering.
class TestVideoFunctions(unittest.TestCase):

    def test_get_playlist_items(self):
        r = main.get_playlist_items(TEST_PLAYLIST)
        self.assertEqual(len(r['items']), 5)

    def test_filter_items_by_timestamp(self):
        r = main.get_playlist_items(TEST_PLAYLIST)
        filtered = main.filter_playlist_items_by_timestamp(r, 1617985920)
        self.assertEqual(len(filtered), 2)


# Not a test, but used in tests below.
def get_playlist_item_embed(pos: int):
    r = main.get_playlist_items(TEST_PLAYLIST)

    playlist_item = r['items'][pos]
    epoch = main.iso_string_to_epoch(playlist_item
                                     ['snippet']['publishedAt'])
    playlist_item['snippet']['publishedAt'] = epoch

    embed = main.video_info_to_embed(playlist_item)
    return embed


# Testing stuff with the Discord Embeds.
class TestEmbeds(unittest.TestCase):

    def test_maxres_thumbnail(self):
        embed = get_playlist_item_embed(1)
        self.assertRegex(embed.thumbnail['url'], '(maxresdefault)')

    def test_hq_thumbnail_when_no_maxres(self):
        embed = get_playlist_item_embed(2)
        self.assertRegex(embed.thumbnail['url'], '(hqdefault)')


if __name__ == '__main__':
    unittest.main()
