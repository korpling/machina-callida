import {Component, OnInit} from '@angular/core';
import {NavController} from '@ionic/angular';
import {ExerciseService} from 'src/app/exercise.service';
import {HelperService} from '../helper.service';

@Component({
    selector: 'app-kwic',
    templateUrl: './kwic.page.html',
    styleUrls: ['./kwic.page.scss'],
})
export class KwicPage implements OnInit {

    public svgElementSelector = '#svg';

    constructor(public navCtrl: NavController,
                public exerciseService: ExerciseService,
                public helperService: HelperService) {
    }

    public initVisualization() {
        document.querySelector(this.svgElementSelector).innerHTML = this.exerciseService.kwicGraphs;
    }

    ngOnInit(): void {
        setTimeout(this.initVisualization.bind(this), 250);
    }
}
