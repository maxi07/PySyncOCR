from src.helpers.rclone_setup import extract_sharepoint_options


def test_sharepoint_options_extraction():
    # Test the extraction of the sharepoint options
    out = b' Office\r\nFound 3 sites, please select the one you want to use:\r\n0: Office (https://test.sharepoint.com/sites/Office) id=test.sharepoint.com,da8xxx4,9910xxx789e\r\n1: Office-alt (https://test.sharepoint.com/office) id=test.sharepoint.com,20706dxxx5-3a3425796c38,d44xxx7d2\r\n2: Home (https://test.sharepoint.com) id=test.sharepoint.com,207xxx2579'

    result = extract_sharepoint_options(out)
    assert len(result) == 3
    assert result[0] == 'Office (https://test.sharepoint.com/sites/Office)'
    assert result[1] == 'Office-alt (https://test.sharepoint.com/office)'
    assert result[2] == 'Home (https://test.sharepoint.com)'
