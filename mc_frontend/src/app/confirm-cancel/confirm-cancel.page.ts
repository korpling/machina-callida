import {Component} from '@angular/core';
import {HelperService} from '../helper.service';
import {NavController} from '@ionic/angular';

@Component({
    selector: 'app-confirm-cancel',
    templateUrl: './confirm-cancel.page.html',
    styleUrls: ['./confirm-cancel.page.scss'],
})
export class ConfirmCancelPage {

    constructor(public navCtrl: NavController,
                public helperService: HelperService) {
    }

    exit(): void {
        this.helperService.currentPopover.dismiss().then();
        this.helperService.currentPopover = null;
    }

    confirm(): void {
        this.helperService.goToHomePage(this.navCtrl).then();
        this.exit();
    }
}
