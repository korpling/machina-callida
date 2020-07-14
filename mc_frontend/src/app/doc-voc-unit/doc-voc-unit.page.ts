import {Component, OnInit} from '@angular/core';
import {HelperService} from 'src/app/helper.service';
import {NavController} from '@ionic/angular';
import {HttpClient} from '@angular/common/http';
import {TranslateService} from '@ngx-translate/core';
import configMC from '../../configMC';

@Component({
    selector: 'app-doc-voc-unit',
    templateUrl: './doc-voc-unit.page.html',
    styleUrls: ['./doc-voc-unit.page.scss'],
})

export class DocVocUnitPage {
    public configMC = configMC;
    hypothesisIndices: number[] = [...Array(5).keys()];
    questionsIndices: number[] = [...Array(10).keys()];
    sequenceIndices: number[] = [...Array(6).keys()];

    constructor(public navCtrl: NavController,
                public http: HttpClient,
                public translate: TranslateService,
                public helperService: HelperService) {
    }
}
