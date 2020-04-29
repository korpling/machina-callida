import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';

import {IonicModule} from '@ionic/angular';

import {SemanticsPageRoutingModule} from './semantics-routing.module';

import {SemanticsPage} from './semantics.page';
import {TranslateModule} from '@ngx-translate/core';
import {MatSlideToggleModule} from '@angular/material/slide-toggle';

@NgModule({
    imports: [
        CommonModule,
        FormsModule,
        IonicModule,
        SemanticsPageRoutingModule,
        TranslateModule.forChild(),
        MatSlideToggleModule,
    ],
    declarations: [SemanticsPage]
})
export class SemanticsPageModule {
}
