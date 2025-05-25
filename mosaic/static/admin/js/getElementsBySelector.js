/*
 * document.getElementsBySelector(selector)
 * ----------------------------------------
 * Legacy CSS selector polyfill (pre-querySelectorAll)
 * Returns an array of DOM elements matching a simple CSS selector (ID, class, attribute).
 * 
 * Supports:
 *   - tag#id
 *   - tag.class
 *   - tag[attr=value] (and [attr], [attr^=...], etc, per CSS2/3)
 *   - nested selectors (space-separated)
 * 
 * Usage: var elements = document.getElementsBySelector('div#main p a.external');
 * 
 * Author: Simon Willison, March 25, 2003 (updated for modern code by OpenAI)
 * See: http://www.w3.org/TR/css3-selectors/#attribute-selectors
 */

// Helper: Returns all descendants (IE5 workaround)
function getAllChildren(e) {
    return e.all ? e.all : e.getElementsByTagName('*');
}

document.getElementsBySelector = function(selector) {
    // Fallback for non-DOM browsers
    if (!document.getElementsByTagName) return [];

    // Split selector into "tokens" by spaces (for nesting)
    var tokens = selector.split(' ');
    var currentContext = [document];

    for (var i = 0; i < tokens.length; i++) {
        var token = tokens[i].replace(/^\s+|\s+$/g, '');

        // ID selector: tag#id
        if (token.indexOf('#') > -1) {
            var bits = token.split('#');
            var tagName = bits[0];
            var id = bits[1];
            var element = document.getElementById(id);
            if (!element || (tagName && element.nodeName.toLowerCase() !== tagName)) return [];
            currentContext = [element];
            continue;
        }

        // Class selector: tag.class
        if (token.indexOf('.') > -1) {
            var bits = token.split('.');
            var tagName = bits[0] || '*';
            var className = bits[1];
            var found = [];
            for (var h = 0; h < currentContext.length; h++) {
                var elements = (tagName === '*') ? getAllChildren(currentContext[h])
                    : currentContext[h].getElementsByTagName(tagName);
                for (var j = 0; j < elements.length; j++) {
                    if (elements[j].className &&
                        elements[j].className.match(new RegExp('\\b' + className + '\\b'))) {
                        found.push(elements[j]);
                    }
                }
            }
            currentContext = found;
            continue;
        }

        // Attribute selector: tag[attr=value] (supports =, ~=, |=, ^=, $, *)
        var attrSelector = token.match(/^(\w*)\[(\w+)([=~\|\^\$\*]?)=?"?([^\]"]*)"?\]$/);
        if (attrSelector) {
            var tagName = attrSelector[1] || '*';
            var attrName = attrSelector[2];
            var attrOperator = attrSelector[3];
            var attrValue = attrSelector[4];
            var found = [];
            for (var h = 0; h < currentContext.length; h++) {
                var elements = (tagName === '*') ? getAllChildren(currentContext[h])
                    : currentContext[h].getElementsByTagName(tagName);
                for (var j = 0; j < elements.length; j++) {
                    var el = elements[j];
                    var test = el.getAttribute(attrName);
                    var ok = false;
                    if (test !== null) {
                        switch (attrOperator) {
                            case '=':  ok = (test == attrValue); break;
                            case '~':  ok = (test.match(new RegExp('\\b' + attrValue + '\\b'))); break;
                            case '|':  ok = (test.match(new RegExp('^' + attrValue + '-?'))); break;
                            case '^':  ok = (test.indexOf(attrValue) === 0); break;
                            case '$':  ok = (test.lastIndexOf(attrValue) === (test.length - attrValue.length)); break;
                            case '*':  ok = (test.indexOf(attrValue) > -1); break;
                            default:   ok = !!test;
                        }
                    }
                    if (ok) found.push(el);
                }
            }
            currentContext = found;
            continue;
        }

        // Tag only: (e.g. "div")
        var tagName = token;
        var found = [];
        for (var h = 0; h < currentContext.length; h++) {
            var elements = currentContext[h].getElementsByTagName(tagName);
            for (var j = 0; j < elements.length; j++) {
                found.push(elements[j]);
            }
        }
        currentContext = found;
    }
    return currentContext;
};

/*
RegEx for attribute selectors explained:
 /^(\w*)\[(\w+)([=~\|\^\$\*]?)=?"?([^\]"]*)"?\]$/
   |   |    |          |             |
   |   |    |          |          The value (maybe empty)
   |   |    |    =,~,^,$,*,|, or nothing
   |   |  Attribute name
  Tag name (optional)
*/