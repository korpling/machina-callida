H5P Confirmation Dialog
=======================

Creates a confirmation dialog, which can be set to confirm or cancel
a user action.

## Usage

Init dialog:
```javascript
var dialog = new H5P.ConfirmationDialog(options);
```

Confirmation dialog accepts the following optional options, and will
default to the ones listed here:

```javascript
var options = {
  dialogText: 'Please confirm that you wish to proceed.',
  cancelText: 'Cancel',
  confirmText: 'Confirm'
}
```

Open dialog: 
```javascript
dialog.show();
```

Close dialog:
```javascript
dialog.hide();
```

Listeners can listen for the following events. They are thrown when
corresponding dialog buttons are pressed:
* 'confirmed'
* 'canceled'

A listener would listen to confirmation of dialog the following way:
```javascript
dialog.on('confirmed', function () {
  // Do something here
});
```

## License

(The MIT License)

Copyright (c) 2012-2014 Amendor AS
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
